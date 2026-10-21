#!/usr/bin/env python3
# Merged Free Fire Bot – Safe Login (Script 3) + Script 1 Features + Flask API + Multi-Account

import sys
import os
import json
import asyncio
import aiohttp
import re
import time
import threading
import binascii
import hashlib
import random
import socket
import ssl
import http.client
import gzip
import httpx
from google_play_scraper import app as play_scraper
from io import BytesIO
from datetime import datetime
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
import jwt
import urllib3
from flask import Flask, request, jsonify

# ---------- PROTOBUF IMPORTS (Script 1 PB2 folder) ----------
import Pb2.DEcwHisPErMsG_pb2 as DEcwHisPErMsG_pb2
import Pb2.PorTs_pb2 as PorTs_pb2
import Pb2.sQ_pb2 as sQ_pb2
import Pb2.Team_msg_pb2 as Team_msg_pb2
import thunderFF_pb2
import login_engine  # NORIX.TCP working login flow

# ---------- SCRIPT 3 EMBEDDED PROTOBUF (safe login) ----------
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import runtime_version as _runtime_version
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder

_runtime_version.ValidateProtobufRuntimeVersion(
    _runtime_version.Domain.PUBLIC,
    5, 27, 2,
    '',
    'my_message.proto'
)
_sym_db = _symbol_database.Default()

DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(
    b'\n\x10my_message.proto\">\n\tMyMessage\x12\x0f\n\x07\x66ield21\x18\x15 \x01(\x03\x12\x0f\n\x07\x66ield22\x18\x16 \x01(\x0c\x12\x0f\n\x07\x66ield23\x18\x17 \x01(\x0c\x62\x06proto3'
)
_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'my_message_pb2', _globals)

# ---------- IMPORT xC4 AND xHeaders ----------
from xC4 import *
from xHeaders import *

# ---------- GLOBALS ----------
app = Flask(__name__)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

loop = None
accounts = []

# Diagnostics only: packet metadata, never full payloads or authentication secrets.
def _diag(event, account=None, packet=None, **details):
    stamp = datetime.now().astimezone().isoformat(timespec="seconds")
    who = f" bot={account.account_index} uid={account.uid}" if account else ""
    if packet is not None:
        try:
            raw = bytes(packet)
            details.update({"bytes": len(raw), "header": raw[:2].hex(),
                            "sha256_12": hashlib.sha256(raw).hexdigest()[:12]})
        except Exception:
            details["packet_metadata"] = "unavailable"
    suffix = " ".join(f"{k}={v}" for k, v in details.items())
    print(f"[TCP-DIAG {stamp}] {event}{who}" + (f" {suffix}" if suffix else ""), flush=True)

# Updated OB55 HTTP client / connection configuration (from udp-level-main)
HTTP_TIMEOUT = httpx.Timeout(15.0, connect=10.0)
client = httpx.AsyncClient(timeout=HTTP_TIMEOUT, verify=False, follow_redirects=True)
AES_KEY = b'Yg&tc%DEuh6%Zc^8'
AES_IV = b'6oyZDr22E3ychjM%'
GAME_HEADERS = {
    "User-Agent": "UnityPlayer/2018.4.12f1 (UnityWebRequest/1.0, libcurl/8.5.0-DEV)",
    "Connection": "Keep-Alive",
    "Accept-Encoding": "gzip",
    "Content-Type": "application/x-www-form-urlencoded",
    "Expect": "100-continue",
    "X-Unity-Version": "2018.4.12f1",
    "X-GA-SV": "1789535859",
    "X-GA": "v1 1",
    "ReleaseVersion": "OB55",
}
  # List holding BotAccount instances

# ---------- ACCOUNT STATE CLASS ----------
class BotAccount:
    def __init__(self, uid, password, account_index):
        self.uid = uid
        self.password = password
        self.account_index = account_index

        # State variables isolated per account
        self.target_uid = int(uid)
        self.jwt_token = None
        self.key = None
        self.iv = None
        self.timestamp = None
        self.region = 'ind'

        self.chat_ip = None
        self.chat_port = None
        self.online_ip = None
        self.online_port = None

        self.online_writer = None
        self.whisper_writer = None

        # Concurrency & Distribution tracking
        self.chat_connected = False
        self.online_connected = False
        self.is_busy = False

        # Queue / failover tracking
        self.fail_count = 0         # consecutive connection failures (chat+online)
        self.is_active = False      # currently one of the active slots

# ========== SAFE LOGIN FUNCTIONS (from Script 3) ==========
async def encrypt_plaintext(plaintext, key, iv):
    cipher = AES.new(key, AES.MODE_CBC, iv)
    return cipher.encrypt(pad(plaintext, AES.block_size))

async def GeT_Key_Iv(serialized_data):
    my_message = _globals['MyMessage']()
    my_message.ParseFromString(serialized_data)
    timestamp, key, iv = my_message.field21, my_message.field22, my_message.field23
    timestamp_obj = Timestamp()
    timestamp_obj.FromNanoseconds(timestamp)
    timestamp_seconds = timestamp_obj.seconds
    timestamp_nanos = timestamp_obj.nanos
    combined_timestamp = timestamp_seconds * 1_000_000_000 + timestamp_nanos
    return combined_timestamp, key, iv

async def Guest_GeneRaTe(uid, password, retry_count=0):
    url = "https://100067.connect.garena.com/oauth/guest/token/grant"
    headers = {
        "Host": "100067.connect.garena.com",
        "User-Agent": "Dalvik/2.1.0 (Linux; U; Android 13; SM-A546E Build/TP1A.220624.014)",
        "Content-Type": "application/x-www-form-urlencoded",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "close",
    }
    data = {
        "uid": f"{uid}",
        "password": f"{password}",
        "response_type": "token",
        "client_type": "2",
        "client_secret": "2ee44819e9b4598845141067b281621874d0d5d7af9d8f7e00c1e54715b7d1e3",
        "client_id": "100067",
    }
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, data=data, timeout=5) as resp:
                if resp.status == 200:
                    resp_data = await resp.json()
                    if 'access_token' in resp_data and 'open_id' in resp_data:
                        return resp_data['access_token'], resp_data['open_id'], resp_data.get("platform", 4)
                    elif resp_data.get('error') == 'error_too_many_requests' or resp_data.get('code') == 1006:
                        wait = min(2 ** retry_count, 32)
                        print(f"[-] Rate limit for {uid}, waiting {wait}s...")
                        await asyncio.sleep(wait)
                        return await Guest_GeneRaTe(uid, password, retry_count + 1)
                    else:
                        print(f"[-] Guest token failed for {uid}: {resp_data}")
                        return None, None
                else:
                    print(f"[-] HTTP {resp.status} for {uid}")
                    return None, None, None
    except Exception as e:
        print(f"[-] Token error for {uid}: {e}")
        return None, None, None

async def get_playstore_version():
    try:
        loop_ = asyncio.get_running_loop()
        result = await loop_.run_in_executor(
            None, lambda: play_scraper('com.dts.freefireth', lang='hi', country='id')
        )
        return result.get("version")
    except Exception:
        return None

async def version_config():
    app_version = await get_playstore_version()
    if not app_version:
        return None
    api_url = (
        "https://version.ggwhitehawk.com/live/ver.php"
        f"?version={app_version}"
        "&lang=hi&device=android&channel=android"
        "&appstore=googleplay&region=BD"
        "&whitelist_version=1.3.0&whitelist_sp_version=1.0.0"
    )
    try:
        response = await client.get(api_url)
        response.raise_for_status()
        data = response.json()
        server_url = data.get("server_url")
        remote_version = data.get("remote_version")
        latest_release_version = data.get("latest_release_version")
        if not server_url or not remote_version or not latest_release_version:
            return None
        return latest_release_version, remote_version, server_url
    except Exception as e:
        print(f"[-] Version config error: {e}")
        return None

async def _build_updated_majorlogin_payload(open_id, access_token, platform, client_version):
    """OB55 MajorLogin payload copied to the EmoteBot connection layer from udp-level-main."""
    proto = thunderFF_pb2.MajorLoginReq()
    proto.event_time = str(datetime.now())[:-7]
    proto.game_name = "free fire"
    proto.platform_id = 1 if str(platform) in ["1", "4"] else int(platform)
    proto.client_version = client_version
    proto.client_version_code = "2019121229"

    # Same current connection/device values used by udp-level-main.
    proto.system_software = "Android OS 12 / API-31 (SP1A.210812.016.C2/user.dxu.20260701.180839)"
    proto.system_hardware = "Handheld"
    proto.device_type = "Handheld"
    proto.screen_width = 1600
    proto.screen_height = 900
    proto.screen_dpi = "300"
    proto.processor_details = "x86-64 SSE3 SSE4.1 SSE4.2 AVX | 2400 | 4"
    proto.memory = 5951
    proto.gpu_renderer = "Adreno (TM) 640"
    proto.unique_device_id = "Google|725030d8-6585-4f55-bcca-a6df7e59935b"
    proto.client_ip = "103.145.112.210"

    proto.telecom_operator = "Citycell"
    proto.network_operator_a = "Citycell"
    proto.network_type = "WIFI"
    proto.network_type_a = "WIFI"
    proto.cpu_type = 2
    proto.cpu_architecture = "64"
    proto.gpu_version = "OpenGL ES 3.2"
    proto.graphics_api = "OpenGLES2"
    proto.language = "en"
    proto.open_id = open_id
    proto.open_id_type = str(platform)
    proto.login_open_id_type = int(platform)
    proto.access_token = access_token
    proto.login_by = 3
    proto.platform_sdk_id = 2
    proto.origin_platform_type = str(platform)
    proto.primary_platform_type = str(platform)
    proto.reg_avatar = 1
    proto.channel_type = 3

    proto.memory_available.version = 55
    proto.memory_available.hidden_value = 81
    proto.external_storage_total = 34308
    proto.external_storage_available = 30777
    proto.internal_storage_total = 2519
    proto.internal_storage_available = 243
    proto.game_disk_storage_total = 34308
    proto.game_disk_storage_available = 32224
    proto.external_sdcard_total_storage = 34308
    proto.external_sdcard_avail_storage = 32224
    proto.library_path = "/data/app/~~UKDdGuy32C5yOa0KZe_ROA==/com.dts.freefireth-UAKF1gjDbXSGfpA07JDTKQ==/lib/arm64"
    proto.library_token = "b8e0cd5e295eee42f5860d3c86e483dd|/data/app/~~UKDdGuy32C5yOa0KZe_ROA==/com.dts.freefireth-UAKF1gjDbXSGfpA07JDTKQ==/base.apk"
    proto.client_using_version = "7428b253defc164018c604a1ebbfebdf"
    proto.supported_astc_bitset = 4095
    proto.analytics_detail = b"FwQVTgUPX1UaUllDDwcWCRBpWAUOUgsvA1snWlBaO1kFYg=="
    proto.loading_time = 14582
    proto.release_channel = "android"
    proto.extra_info = "KqsHT4tDHGqm9PQ3syB24XA4N6SWy/Q/HfMFTQM+SgxmVqsgPK138ajtCFyVNW/Q7p6hxoenpRjeZ2NphiIosCZ3YDkONB5NAa+zTwNo7iabx/mj"
    proto.android_engine_init_flag = 111207
    proto.if_push = 1
    proto.is_vpn = 0

    return AES.new(AES_KEY, AES.MODE_CBC, AES_IV).encrypt(
        pad(proto.SerializeToString(), AES.block_size)
    )

async def ToKen_GeneRaTe(Access_ToKen, Access_Uid, platform=4):
    try:
        cfg = await version_config()
        if not cfg:
            return None
        release_version, client_version, server_url = cfg
        payload = await _build_updated_majorlogin_payload(
            Access_Uid and Access_Uid, Access_ToKen, platform, client_version
        )

        req_headers = GAME_HEADERS.copy()
        req_headers["ReleaseVersion"] = release_version
        response = await client.post(f"{server_url.rstrip('/')}/MajorLogin", headers=req_headers, content=payload)
        if response.status_code != 200:
            print(f"[-] MajorLogin failed: HTTP {response.status_code}")
            return None
        response_content = response.content
        if len(response_content) < 40:
            return None

        # OB55 response may have a transport prefix; try direct + offsets like udp-level-main.
        res_proto = None
        for offset in [0, 64] + list(range(0, min(128, len(response_content)))):
            try:
                candidate = thunderFF_pb2.MajorLoginRes()
                candidate.ParseFromString(response_content[offset:])
                if candidate.region and candidate.token:
                    res_proto = candidate
                    break
            except Exception:
                continue
        if res_proto is None:
            return None

        timestamp = res_proto.server_time
        key = bytes(res_proto.aes_ak)
        iv = bytes(res_proto.iv_i)
        if not key or not iv:
            print("[-] MajorLogin response did not contain aes_ak/iv_i")
            return None

        # GetLoginData must use the JWT and the URL returned by MajorLogin.
        gl = await GeT_LoGin_PorTs(res_proto.token, payload, release_version, res_proto.url)
        if not gl:
            return None
        ip, port, ip2, port2 = gl
        return res_proto.token, key, iv, timestamp, ip, port, ip2, port2, res_proto.url
    except Exception as e:
        print(f"[-] Token generation error: {e}")
        return None

async def GeT_LoGin_PorTs(JwT_ToKen, PayLoad, release_version="OB55", base_url=None):
    """GetLoginData handling matched to udp-level-main.

    OB55 GetLoginDataRes defines functional_addrs and informational_addrs
    as scalar strings (not repeated fields).
    """
    try:
        if not base_url:
            print("[-] GetLoginData: MajorLogin returned no URL")
            return None, None, None, None

        url = f"{base_url.rstrip('/')}/GetLoginData"
        req_headers = GAME_HEADERS.copy()
        req_headers["ReleaseVersion"] = release_version
        req_headers["Authorization"] = f"Bearer {JwT_ToKen}"
        req_headers["Host"] = "clientbp.ppmainecoonghj.com"

        response = await client.post(url, headers=req_headers, content=PayLoad)
        if response.status_code != 200:
            print(f"[-] GetLoginData HTTP {response.status_code} from {url}")
            return None, None, None, None

        content = response.content
        if not content:
            print("[-] GetLoginData returned empty response")
            return None, None, None, None

        # This is the same protobuf used by udp-level-main.
        # IMPORTANT: both fields are strings, so do NOT call list() on them.
        info_addr = ""
        func_addr = ""

        for offset in range(min(128, len(content))):
            try:
                candidate = thunderFF_pb2.GetLoginDataRes()
                candidate.ParseFromString(content[offset:])
                if candidate.functional_addrs or candidate.informational_addrs:
                    info_addr = candidate.informational_addrs
                    func_addr = candidate.functional_addrs
                    break
            except Exception:
                continue

        # Exact full-response attempt as used by udp-level-main.
        if not (info_addr or func_addr):
            try:
                candidate = thunderFF_pb2.GetLoginDataRes()
                candidate.ParseFromString(content)
                info_addr = candidate.informational_addrs
                func_addr = candidate.functional_addrs
            except Exception:
                pass

        def parse_addr(value):
            if not isinstance(value, str) or not value:
                return None
            value = value.strip()
            # Normally each protobuf field is exactly host:port.
            try:
                host, port = value.rsplit(":", 1)
                if host and port.isdigit():
                    return host, int(port)
            except Exception:
                pass
            return None

        chat = parse_addr(info_addr)
        online = parse_addr(func_addr)

        # Legacy encrypted-packet fallback only if the new protobuf fields
        # could not be extracted.
        if chat is None or online is None:
            try:
                decoded = await DeCode_PackEt(content.hex())
                if decoded:
                    data = json.loads(decoded)
                    a_chat = data.get('32', {}).get('data')
                    a_online = data.get('14', {}).get('data')
                    if chat is None:
                        chat = parse_addr(a_chat)
                    if online is None:
                        online = parse_addr(a_online)
            except Exception as e:
                print(f"[-] GetLoginData legacy decode failed: {e}")

        if chat is None or online is None:
            print("[-] GetLoginData returned no usable chat/online addresses")
            print(f"[-] functional_addrs={func_addr!r}")
            print(f"[-] informational_addrs={info_addr!r}")
            print(f"[-] Response length: {len(content)} bytes")
            return None, None, None, None

        # EmoteBot expects chat first, online second.
        return chat[0], chat[1], online[0], online[1]
    except Exception as e:
        print(f"[-] GetLoginData error: {e}")
        return None, None, None, None

# ========== TCP FUNCTIONS (from Script 1) ==========
async def xAuThSTarTuP(TarGeT, token, timestamp, key, iv):
    uid_hex = hex(TarGeT)[2:]
    uid_length = len(uid_hex)
    encrypted_timestamp = await DecodE_HeX(timestamp)
    encrypted_account_token = token.encode().hex()
    encrypted_packet = await EnC_PacKeT(encrypted_account_token, key, iv)
    encrypted_packet_length = hex(len(encrypted_packet) // 2)[2:]
    if uid_length == 9: headers = '0000000'
    elif uid_length == 8: headers = '00000000'
    elif uid_length == 10: headers = '000000'
    elif uid_length == 7: headers = '000000000'
    else: headers = '0000000'
    return f"0115{headers}{uid_hex}{encrypted_timestamp}00000{encrypted_packet_length}{encrypted_packet}"

async def cHTypE(H):
    if not H: return 'Squid'
    elif H == 1: return 'CLan'
    elif H == 2: return 'PrivaTe'

async def SEndMsG(H, message, Uid, chat_id, key, iv):
    TypE = await cHTypE(H)
    if TypE == 'Squid': msg_packet = await xSEndMsgsQ(message, chat_id, key, iv)
    elif TypE == 'CLan': msg_packet = await xSEndMsg(message, 1, chat_id, chat_id, key, iv)
    elif TypE == 'PrivaTe': msg_packet = await xSEndMsg(message, 2, Uid, Uid, key, iv)
    return msg_packet

def _norix_build_ob55_online_auth(account_uid, token, kts, key, iv):
    """Exact online auth builder from NORIX.TCP/bot_core.py."""
    token_bytes = token.encode("utf-8")
    cipher = AES.new(key, AES.MODE_CBC, iv)
    enc_token = cipher.encrypt(pad(token_bytes, 16))
    opcode = bytes.fromhex("830c")
    uid_bytes = int(account_uid).to_bytes(8, byteorder="big")
    kts_bytes = int(kts).to_bytes(4, byteorder="big")
    len_bytes = len(enc_token).to_bytes(8, byteorder="big")
    return opcode + uid_bytes + kts_bytes + len_bytes + enc_token, enc_token


def _norix_create_auth_token_chat(account_id, jwt_token, timestamp, key, iv):
    """Exact chat auth builder from NORIX.TCP/bot_core.py."""
    K = bytes.fromhex(key) if isinstance(key, str) else key
    V = bytes.fromhex(iv) if isinstance(iv, str) else iv
    jwt_bytes = jwt_token.encode("utf-8")
    ct = AES.new(K, AES.MODE_CBC, V).encrypt(pad(jwt_bytes, AES.block_size))
    uid_b = int(account_id).to_bytes(8, "big")
    ts_b = int(timestamp).to_bytes(4, "big")
    len_b = len(ct).to_bytes(4, "big")
    header = bytes.fromhex("6d19") + uid_b + ts_b + len_b
    return (header + ct).hex()


async def build_tcp_startup_packet(account_id, token, server_time, key, iv, region="BD", typ="OnLine"):
    """Build the same OB55 TCP startup packet used by udp-level-main.
    Online and Chat/Informational gateways require different prefixes.
    """
    uid_hex = f"{int(account_id):016x}"
    timestamp_hex = f"{int(server_time):08x}"
    encrypted_packet = (await encrypt_plaintext(token.encode(), key, iv)).hex()
    encrypted_packet_length = f"{len(encrypted_packet) // 2:08x}"
    reg = str(region or "BD").upper()
    if typ == "OnLine":
        prefix = "7119" if reg == "BD" else ("7114" if reg == "IND" else "7115")
        return f"{prefix}{uid_hex}{timestamp_hex}00000000{encrypted_packet_length}{encrypted_packet}"
    prefix = "9219" if reg == "BD" else ("9214" if reg == "IND" else "9215")
    return f"{prefix}{uid_hex}{timestamp_hex}{encrypted_packet_length}{encrypted_packet}"

async def _send_connection_keepalive(writer, region="BD"):
    """OB55 TCP keepalive pulse used by udp-level-main.
    Keeps the game gateway session active while there is no application traffic.
    """
    try:
        reg = str(region or "BD").upper()
        pulse = bytes.fromhex("0219" if reg == "BD" else ("0214" if reg == "IND" else "0215"))
        if writer and not writer.is_closing():
            writer.write(pulse)
            await writer.drain()
            return True
    except Exception:
        pass
    return False


async def SEndPacKeT(account: BotAccount, TypE, PacKeT):
    try:
        if TypE == 'ChaT' and account.whisper_writer:
            _diag("send", account, PacKeT, channel="chat")
            account.whisper_writer.write(PacKeT)
            await account.whisper_writer.drain()
        elif TypE == 'OnLine' and account.online_writer:
            _diag("send", account, PacKeT, channel="online")
            account.online_writer.write(PacKeT)
            await account.online_writer.drain()
        else:
            pass
    except Exception as e:
        print(f"[Bot {account.account_index}] Error sending packet ({TypE}): {e}")

async def TcPOnLine(account: BotAccount, startup_packet, reconnect_delay=1.0):
    """Keep the OB55 Online TCP gateway alive using udp-level-main's flow."""
    while True:
        reader = writer = None
        ping_task = None
        try:
            reader, writer = await asyncio.open_connection(
                account.online_ip, int(account.online_port)
            )
            raw_sock = writer.get_extra_info("socket")
            if raw_sock:
                try:
                    raw_sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
                    raw_sock.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
                    raw_sock.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, 65536)
                    raw_sock.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 65536)
                except Exception:
                    pass

            account.online_writer = writer
            account.online_connected = True
            print(f"[Bot {account.account_index}] Online connected to {account.online_ip}:{account.online_port}")
            _diag("connected", account, channel="online", endpoint=f"{account.online_ip}:{account.online_port}")

            startup_bytes = bytes.fromhex(startup_packet)
            _diag("send_auth_startup", account, startup_bytes, channel="online")
            writer.write(startup_bytes)
            await writer.drain()

            # DISABLED: NORIX.TCP (working) sends only the auth packet on the online socket,
            # no extra keepalive pulses. Block below kept for reference.
            # # Same 2-byte OB55 pulse used by udp-level-main.
            # pulse = bytes.fromhex(
                # "0219" if str(account.region).upper() == "BD"
                # else ("0214" if str(account.region).upper() == "IND" else "0215")
            # )
            # _diag("send_keepalive", account, pulse, channel="online", timing="immediate")
            # writer.write(pulse)
            # await writer.drain()

            # async def info_keepalive():
                # while True:
                    # await asyncio.sleep(5)
                    # if writer.is_closing():
                        # return
                    # try:
                        # _diag("send_keepalive", account, pulse, channel="online", timing="periodic")
                        # writer.write(pulse)
                        # await writer.drain()
                    # except Exception:
                        # return

            # ping_task = asyncio.create_task(info_keepalive())

            while True:
                data2 = await reader.read(8192)
                if not data2:
                    _diag("connection_closed_by_peer", account, channel="online")
                    raise ConnectionError("Online gateway closed the connection")
                _diag("receive", account, data2, channel="online")
                if data2.hex().startswith("0500") and len(data2.hex()) > 1000:
                    try:
                        packet = await DeCode_PackEt(data2.hex()[10:])
                        packet = json.loads(packet)
                        owner_uid, chat_code, squad_code = await GeTSQDaTa(packet)
                        join_chat = await AutH_Chat(3, owner_uid, chat_code, account.key, account.iv)
                        await SEndPacKeT(account, "ChaT", join_chat)
                        message = f"[B][C]{await ArA_CoLor()}\n- WeLComE To Emote Bot ! "
                        p = await SEndMsG(0, message, owner_uid, owner_uid, account.key, account.iv)
                        await SEndPacKeT(account, "ChaT", p)
                    except Exception:
                        pass

        except asyncio.CancelledError:
            raise
        except Exception as e:
            print(f"[Bot {account.account_index}] ErroR With {account.online_ip}:{account.online_port} - {e}")
        finally:
            if ping_task:
                ping_task.cancel()
                try:
                    await ping_task
                except BaseException:
                    pass
            account.online_connected = False
            account.online_writer = None
            if writer:
                try:
                    writer.close()
                    await writer.wait_closed()
                except Exception:
                    pass
        await asyncio.sleep(reconnect_delay)

async def TcPChaT(account: BotAccount, AutHToKen, LoGinDaTaUncRypTinG, ready_event, reconnect_delay=0.5):
    while True:
        try:
            reader, writer = await asyncio.open_connection(account.chat_ip, int(account.chat_port))
            account.whisper_writer = writer
            account.chat_connected = True
            
            bytes_payload = bytes.fromhex(AutHToKen)
            account.whisper_writer.write(bytes_payload)
            await account.whisper_writer.drain()
            
            if not ready_event.is_set():
                ready_event.set()
                
            print(f"[Bot {account.account_index}] Chat connected to {account.chat_ip}:{account.chat_port}")
            _diag("connected", account, channel="chat", endpoint=f"{account.chat_ip}:{account.chat_port}")
            
            if LoGinDaTaUncRypTinG.Clan_ID:
                clan_id = LoGinDaTaUncRypTinG.Clan_ID
                clan_compiled_data = LoGinDaTaUncRypTinG.Clan_Compiled_Data
                pK = await AuthClan(clan_id, clan_compiled_data, account.key, account.iv)
                if account.whisper_writer:
                    account.whisper_writer.write(pK)
                    await account.whisper_writer.drain()
                    
            while True:
                data = await reader.read(9999)
                if not data:
                    _diag("connection_closed_by_peer", account, channel="chat")
                    break
                _diag("receive", account, data, channel="chat")
                
                if data.hex().startswith("120000"):
                    msg = await DeCode_PackEt(data.hex()[10:])
                    chatdata = json.loads(msg)
                    try:
                        response = await DecodeWhisperMessage(data.hex()[10:])
                        uid = response.Data.uid
                        chat_id = response.Data.Chat_ID
                        XX = response.Data.chat_type
                        inPuTMsG = response.Data.msg.lower()
                    except:
                        response = None

                    if response:
                        # /f command
                        if inPuTMsG.strip().startswith('/f'):
                            try:
                                dd = chatdata['5']['data']['16']
                                message = f"[B][C]{await ArA_CoLor()}\n\nOnLy In SQuaD !"
                                P = await SEndMsG(response.Data.chat_type, message, uid, chat_id, account.key, account.iv)
                                await SEndPacKeT(account, 'ChaT', P)
                            except:
                                parts = inPuTMsG.strip().split()
                                message = f'[B][C]{await ArA_CoLor()}\nACITVE TarGeT -> {xMsGFixinG(uid)}\n'
                                P = await SEndMsG(response.Data.chat_type, message, uid, chat_id, account.key, account.iv)
                                await SEndPacKeT(account, 'ChaT', P)
                                uid_list = []
                                idT = None
                                for part in parts[1:]:
                                    try:
                                        uid_list.append(int(part))
                                    except:
                                        try: idT = int(part)
                                        except: pass
                                if idT is None:
                                    idT = uid_list.pop() if uid_list else 909000001
                                for i in range(200):
                                    for u in uid_list:
                                        H = await Emote_k(u, idT, account.key, account.iv, account.region)
                                        await SEndPacKeT(account, 'OnLine', H)
                                    await asyncio.sleep(0.08)

                        # /d command
                        if inPuTMsG.strip().startswith('/d'):
                            try:
                                dd = chatdata['5']['data']['16']
                                message = f"[B][C]{await ArA_CoLor()}\n\nOnLy In SQuaD !"
                                P = await SEndMsG(response.Data.chat_type, message, uid, chat_id, account.key, account.iv)
                                await SEndPacKeT(account, 'ChaT', P)
                            except:
                                parts = inPuTMsG.strip().split()
                                message = f'[B][C]{await ArA_CoLor()}\nACITVE TarGeT -> {xMsGFixinG(uid)}\n'
                                P = await SEndMsG(response.Data.chat_type, message, uid, chat_id, account.key, account.iv)
                                await SEndPacKeT(account, 'ChaT', P)
                                uid_list = []
                                idT = None
                                for part in parts[1:]:
                                    try: uid_list.append(int(part))
                                    except:
                                        try: idT = int(part)
                                        except: pass
                                if idT is None:
                                    idT = uid_list.pop() if uid_list else 909000001
                                for u in uid_list:
                                    H = await Emote_k(u, idT, account.key, account.iv, account.region)
                                    await SEndPacKeT(account, 'OnLine', H)

                        # /s command
                        if inPuTMsG.strip().startswith('/s'):
                            EM = await FS(account.key, account.iv)
                            await SEndPacKeT(account, 'OnLine', EM)

                        # /x/ command
                        if inPuTMsG.startswith('/x/'):
                            CodE = inPuTMsG.split('/x/')[1]
                            try:
                                dd = chatdata['5']['data']['16']
                                EM = await GenJoinSquadsPacket(CodE, account.key, account.iv)
                                await SEndPacKeT(account, 'OnLine', EM)
                            except: pass

                        # leave command
                        if inPuTMsG == 'leave':
                            leave = await ExiT(account.target_uid, account.key, account.iv)
                            await SEndPacKeT(account, 'OnLine', leave)

                        # /5 command
                        if inPuTMsG.startswith("/5"):
                            try:
                                dd = chatdata['5']['data']['16']
                                message = f"[B][C]{await ArA_CoLor()}\n\nAccepT My InV FasT"
                                P = await SEndMsG(response.Data.chat_type, message, uid, chat_id, account.key, account.iv)
                                await SEndPacKeT(account, 'ChaT', P)
                                PAc = await OpEnSq(account.key, account.iv, account.region)
                                await SEndPacKeT(account, 'OnLine', PAc)
                                C = await cHSq(5, uid, account.key, account.iv, account.region)
                                await asyncio.sleep(0.5)
                                await SEndPacKeT(account, 'OnLine', C)
                                V = await SEnd_InV(5, uid, account.key, account.iv, account.region)
                                await asyncio.sleep(0.5)
                                await SEndPacKeT(account, 'OnLine', V)
                                E = await ExiT(account.target_uid, account.key, account.iv)
                                await asyncio.sleep(3)
                                await SEndPacKeT(account, 'OnLine', E)
                            except: pass

                        # help command
                        if inPuTMsG in ("dev", "help"):
                            message = '/d <uids> <id> /f <uids> <id> for fast emote'
                            P = await SEndMsG(response.Data.chat_type, message, uid, chat_id, account.key, account.iv)
                            await SEndPacKeT(account, 'ChaT', P)
                            
            account.whisper_writer.close()
            await account.whisper_writer.wait_closed()
            
        except Exception as e:
            print(f"[Bot {account.account_index}] ErroR Chat {account.chat_ip}:{account.chat_port} - {e}")
        finally:
            account.whisper_writer = None
            account.chat_connected = False
            
        await asyncio.sleep(reconnect_delay)

# ========== DECODE FUNCTIONS ==========
async def DecodeWhisperMessage(hex_packet):
    packet = bytes.fromhex(hex_packet)
    proto = DEcwHisPErMsG_pb2.DecodeWhisper()
    proto.ParseFromString(packet)
    return proto

async def decode_team_packet(hex_packet):
    packet = bytes.fromhex(hex_packet)
    proto = sQ_pb2.recieved_chat()
    proto.ParseFromString(packet)
    return proto

# ========== FLASK API ==========
async def perform_emote(account: BotAccount, team_code: str, uids: list, emote_id: int):
    try:
        if not account.online_connected or not account.online_writer:
            raise Exception("Selected bot online connection dropped")

        _diag("action_start", account, action="join_emote_leave", targets=len(uids), emote_id=emote_id)
        EM = await GenJoinSquadsPacket(team_code, account.key, account.iv)
        _diag("stage_join", account, EM, builder="GenJoinSquadsPacket", team_code_length=len(str(team_code)))
        await SEndPacKeT(account, 'OnLine', EM)
        await asyncio.sleep(1.0)

        for uid_str in uids:
            uid = int(uid_str)
            H = await Emote_k(uid, emote_id, account.key, account.iv, account.region)
            _diag("stage_emote", account, H, target_uid=uid)
            await SEndPacKeT(account, 'OnLine', H)

        await asyncio.sleep(0.5)
        LV = await ExiT(account.target_uid, account.key, account.iv)
        _diag("stage_leave", account, LV)
        await SEndPacKeT(account, 'OnLine', LV)
        _diag("action_packets_sent", account, action="join_emote_leave")
        return {"status": "success"}
    except Exception as e:
        _diag("action_error", account, error=type(e).__name__, message=str(e)[:180])
        print(f"[Bot {account.account_index}] Perform emote error: {e}")
        raise
    finally:
        account.is_busy = False
        _diag("action_finished", account, busy=False)

@app.route('/bots')
@app.route('/status')
def status():
    status_list = []
    for acc in accounts:
        status_list.append({
            "account_number": acc.account_index,
            "uid": acc.uid,
            "target_uid": acc.target_uid,
            "chat_connected": acc.chat_connected,
            "online_connected": acc.online_connected,
            "is_busy": acc.is_busy
        })
    return jsonify({"total_bots": len(accounts), "bots": status_list})

@app.route('/join')
def join_team():
    global loop
    team_code = request.args.get('tc')
    uid1 = request.args.get('uid1')
    uid2 = request.args.get('uid2')
    uid3 = request.args.get('uid3')
    uid4 = request.args.get('uid4')
    uid5 = request.args.get('uid5')
    uid6 = request.args.get('uid6')
    emote_id_str = request.args.get('emote_id')

    if not team_code or not emote_id_str:
        return jsonify({"status": "error", "message": "Missing tc or emote_id"})

    try: emote_id = int(emote_id_str)
    except: return jsonify({"status": "error", "message": "emote_id must be integer"})

    uids = [uid for uid in [uid1, uid2, uid3, uid4, uid5, uid6] if uid]
    if not uids:
        return jsonify({"status": "error", "message": "Provide at least one UID"})

    # Request distribution strategy: Find first available bot
    available_account = None
    for acc in accounts:
        if acc.online_connected and acc.chat_connected and not acc.is_busy:
            available_account = acc
            break

    if not available_account:
        return jsonify({"status": "error", "message": "No available bots at the moment"})

    # Mark as busy so it doesn't get scheduled simultaneously 
    available_account.is_busy = True
    
    future = asyncio.run_coroutine_threadsafe(
        perform_emote(available_account, team_code, uids, emote_id), loop
    )
    def _log_action_future(done_future):
        try:
            done_future.result()
        except Exception as exc:
            _diag("request_task_failed", available_account, error=type(exc).__name__, message=str(exc)[:180])
    future.add_done_callback(_log_action_future)

    return jsonify({
        "status": "success",
        "assigned_bot": available_account.account_index,
        "team_code": team_code,
        "uids": uids,
        "emote_id": emote_id_str,
        "message": "Emote triggered"
    })

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port, debug=False, use_reloader=False)

# ========== BOT PER-ACCOUNT RUNNER ==========
async def bot_login_and_connect(account: BotAccount):
    print(f"[Bot {account.account_index}] Starting login for {account.uid}")

    # Use NORIX.TCP's working end-to-end login, not Emote Bot's older
    # MajorLogin payload that was returning HTTP 400.
    result = await login_engine.do_login(
        account.uid, account.password, str(account.region or "IND").upper()
    )
    if not result:
        print(f"[Bot {account.account_index}] NORIX login failed")
        return None

    account.target_uid = int(result["bot_uid"])
    account.jwt_token = result["token"]
    account.key = result["key"]
    account.iv = result["iv"]
    account.timestamp = int(result["timestamp"])
    account.region = str(result["region"] or account.region).upper()
    account.chat_ip = result["chat_ip"]
    account.chat_port = int(result["chat_port"])
    account.online_ip = result["online_ip"]
    account.online_port = int(result["online_port"])

    print(
        f"[Bot {account.account_index}] NORIX login OK | UID: {account.target_uid} "
        f"| Region: {account.region} | Chat: {account.chat_ip}:{account.chat_port} "
        f"| Online: {account.online_ip}:{account.online_port}"
    )

    # Use NORIX's exact TCP authentication packets for both gateways.
    online_auth, _ = _norix_build_ob55_online_auth(
        account.target_uid, account.jwt_token, account.timestamp,
        account.key, account.iv
    )
    online_startup = online_auth.hex()
    chat_startup = _norix_create_auth_token_chat(
        account.target_uid, account.jwt_token, account.timestamp,
        account.key, account.iv
    )

    class DummyLoginData:
        Clan_ID = None
        Clan_Compiled_Data = None

    LoGinDaTaUncRypTinG = DummyLoginData()
    ready_event = asyncio.Event()

    task1 = asyncio.create_task(
        TcPChaT(account, chat_startup, LoGinDaTaUncRypTinG, ready_event)
    )

    await ready_event.wait()
    await asyncio.sleep(1)

    task2 = asyncio.create_task(
        TcPOnLine(account, online_startup)
    )

    print(f"\n[Bot {account.account_index}] STarTinG And OnLine on TarGet: {account.target_uid}")
    
    await asyncio.gather(task1, task2)

async def run_account_loop(account: BotAccount):
    """Loop for an ACTIVE account. On 5 consecutive failures, mark as failed and wake the manager."""
    MAX_FAILS = 5
    while True:
        try:
            await asyncio.wait_for(bot_login_and_connect(account), timeout=7 * 60 * 60)
            # Successful run — reset fail counter
            account.fail_count = 0
        except asyncio.TimeoutError:
            print(f"[Bot {account.account_index}] Token ExpiRed! ResTartinG...")
            account.fail_count = 0  # timeout is normal expiry, not a failure
        except asyncio.CancelledError:
            # Task cancelled by queue manager — stop cleanly
            account.is_active = False
            print(f"[Bot {account.account_index}] Deactivated (moved to queue).")
            return
        except Exception as e:
            account.fail_count += 1
            print(f"[Bot {account.account_index}] ErroR TcP - {e} => ResTarTinG... (fail {account.fail_count}/{MAX_FAILS})")
            if account.fail_count >= MAX_FAILS:
                account.is_active = False
                print(f"[Bot {account.account_index}] Reached {MAX_FAILS} failures — marking as FAILED.")
                # Signal the queue manager
                if _queue_event is not None:
                    _queue_event.set()
                return

        await asyncio.sleep(5) # Delay before reconnecting a failed account

# ========== QUEUE MANAGER ==========
_queue_event: asyncio.Event = None

async def queue_manager(active_limit: int, all_accounts: list):
    """
    Watches the active pool. When an active bot fails (is_active=False),
    pulls the same number of replacements from the queue (inactive bots).
    Never exceeds active_limit concurrent bots.
    """
    global _queue_event
    _queue_event = asyncio.Event()

    active_tasks: dict = {}   # account_index -> asyncio.Task

    # Bootstrap: activate the first `active_limit` accounts
    queue = list(all_accounts)  # order preserved; front = next to activate
    to_activate = queue[:active_limit]
    queue = queue[active_limit:]

    for acc in to_activate:
        acc.is_active = True
        t = asyncio.create_task(run_account_loop(acc))
        active_tasks[acc.account_index] = t
        print(f"[Queue] Activated Bot {acc.account_index} (uid={acc.uid})")

    print(f"[Queue] {len(active_tasks)} active / {len(queue)} in queue  (limit={active_limit})")

    while True:
        await _queue_event.wait()
        _queue_event.clear()

        # Find slots that have gone inactive (failed)
        failed = [acc for acc in all_accounts if not acc.is_active and acc.account_index in active_tasks]
        for acc in failed:
            t = active_tasks.pop(acc.account_index, None)
            if t and not t.done():
                t.cancel()
                try:
                    await t
                except (asyncio.CancelledError, Exception):
                    pass
            print(f"[Queue] Bot {acc.account_index} removed from active pool.")

        # Fill empty slots from queue
        slots_needed = active_limit - len(active_tasks)
        if slots_needed > 0 and queue:
            fill = queue[:slots_needed]
            queue = queue[slots_needed:]
            for acc in fill:
                acc.is_active = True
                acc.fail_count = 0
                t = asyncio.create_task(run_account_loop(acc))
                active_tasks[acc.account_index] = t
                print(f"[Queue] Promoted Bot {acc.account_index} (uid={acc.uid}) from queue  "
                      f"({len(active_tasks)} active / {len(queue)} remaining in queue)")
        elif slots_needed > 0:
            print(f"[Queue] {slots_needed} slot(s) empty but queue is exhausted.")

        # Clean up any tasks that finished on their own
        for idx in list(active_tasks.keys()):
            if active_tasks[idx].done():
                active_tasks.pop(idx)

# ========== MAIN ENTRY ==========
def load_accounts(filename='bot.txt'):
    """
    Parse bot.txt.
    Optional first line: active=<N>   (sets the concurrent active limit)
    Remaining lines: uid:password
    Returns (active_limit, [BotAccount, ...])
    """
    active_limit = None
    accs = []
    if not os.path.exists(filename):
        print(f"[-] Credentials file '{filename}' not found.")
        return active_limit, accs
    with open(filename, 'r') as f:
        lines = f.read().splitlines()

    account_index = 1
    for line in lines:
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        # Check for active=N directive
        if line.lower().startswith('active='):
            try:
                active_limit = int(line.split('=', 1)[1].strip())
            except ValueError:
                print(f"[!] Invalid active= value: {line}")
            continue
        if ':' in line:
            uid, pwd = line.split(':', 1)
            accs.append(BotAccount(uid.strip(), pwd.strip(), account_index))
            account_index += 1

    return active_limit, accs

async def StarTinG():
    global loop, accounts
    loop = asyncio.get_running_loop()

    active_limit, accounts = load_accounts()
    if not accounts:
        print("[-] No accounts loaded. Exiting.")
        return

    print(f"[+] Loaded {len(accounts)} accounts.")

    if active_limit is not None and active_limit > 0:
        effective_limit = min(active_limit, len(accounts))
        print(f"[+] Active limit from bot.txt: {active_limit}  "
              f"(effective: {effective_limit}, queue size: {len(accounts) - effective_limit})")
    else:
        effective_limit = len(accounts)
        print(f"[+] No active= limit set — running all {effective_limit} bots.")

    # Start Flask API in a daemon thread
    flask_thread = threading.Thread(target=run_flask, daemon=True)
    flask_thread.start()

    # Run queue manager (handles activation, failover, limits)
    await queue_manager(effective_limit, accounts)

if __name__ == '__main__':
    asyncio.run(StarTinG())
