#!/usr/bin/env python3
# Merged Free Fire Bot – Safe Login (Script 3) + Script 1 Features + Flask API

import sys
import os
import json
import asyncio
import aiohttp
import re
import time
import threading
import binascii
import random
import socket
import ssl
import http.client
import gzip
from io import BytesIO
from datetime import datetime
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
import jwt
import urllib3
from flask import Flask, request, jsonify

# ---------- PROTOBUF IMPORTS (Script 1 PB2 folder) ----------
import Pb2.DEcwHisPErMsG_pb2 as DEcwHisPErMsG_pb2
import Pb2.MajoRLoGinrEq_pb2 as MajoRLoGinrEq_pb2
import Pb2.MajoRLoGinrEs_pb2 as MajoRLoGinrEs_pb2
import Pb2.PorTs_pb2 as PorTs_pb2
import Pb2.sQ_pb2 as sQ_pb2
import Pb2.Team_msg_pb2 as Team_msg_pb2

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
online_writer = None
whisper_writer = None
spam_room = False
spammer_uid = None
spam_chat_id = None
spam_uid = None
Spy = False
Chat_Leave = False
BOT_UID = 16928690747  # Changed to your bot UID
loop = None

app = Flask(__name__)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# ========== SAFE LOGIN FUNCTIONS (from Script 3) ==========
async def encrypt_plaintext(plaintext):
    cipher = AES.new(Key, AES.MODE_CBC, Iv)
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
        "User-Agent": "Dalvik/2.1.0 (Linux; U; Android 9; G011A Build/PI)",
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
                        return resp_data['access_token'], resp_data['open_id']
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
                    return None, None
    except Exception as e:
        print(f"[-] Token error for {uid}: {e}")
        return None, None

async def ToKen_GeneRaTe(Access_ToKen, Access_Uid):
    try:
        PLaFTrom = "4"
        Version = '2024010012'
        V = '1.126.2'

        PyL = {
            3: str(datetime.now())[:-7],
            4: "free fire",
            5: 2,
            7: V,
            8: "Android OS 11 / API-30 (RQ3A.210805.001)",
            9: "Handheld",
            10: "Verizon",
            11: "WIFI",
            12: 1080,
            13: 2400,
            14: "440",
            15: "ARMv8",
            16: 6144,
            17: "Adreno (TM) 650",
            18: "OpenGL ES 3.2 V@1.50",
            19: "Google|34a7dcdf-a7d5-4cb6-8d7e-3b0e448a0c57",
            20: "",
            21: "en",
            22: Access_Uid,
            23: PLaFTrom,
            24: "Handheld",
            25: "google G011A",
            29: Access_ToKen,
            30: 3,
            41: "Verizon",
            42: "WIFI",
            57: "1ac4b80ecf0478a44203bf8fac6120f5",
            60: 32966,
            61: 29779,
            62: 2479,
            63: 914,
            64: 31176,
            65: 32966,
            66: 31176,
            67: 32966,
            70: 4,
            73: 2,
            74: "/data/app/com.dts.freefireth-g8eDE0T268FtFmnFZ2UpmA==/lib/arm",
            76: 1,
            77: "5b892aaabd688e571f688053118a162b|/data/app/com.dts.freefireth-g8eDE0T268FtFmnFZ2UpmA==/base.apk",
            78: 6,
            79: 1,
            81: "64",
            83: Version,
            86: "OpenGLES3",
            87: 255,
            88: PLaFTrom,
            89: "J\x03FD\x04\r_UH\x03\x0b\x16_\x03D^J>\x0fWT\x00\\=\nQ_;\x00\r;Z\x05a",
            90: "Phoenix",
            91: "AZ",
            92: 10214,
            93: "3rd_party",
            94: "KqsHT7gtKWkK0gY/HwmdwXIhSiz4fQldX3YjZeK86XBTthKAf1bW4Vsz6Di0S8vqr0Jc4HX3TMQ8KaUU3GeVvYzWF9I=",
            95: 111207,
            97: 1,
            98: 1,
            99: f"{PLaFTrom}",
            100: f"{PLaFTrom}"
        }

        PyL = (await CrEaTe_ProTo(PyL)).hex()
        PaYload = bytes.fromhex(await EnC_AEs(PyL))

        context = ssl._create_unverified_context()
        conn = http.client.HTTPSConnection("loginbp.ggpolarbear.com", context=context, timeout=5)
        headers = {
            'X-Unity-Version': '2018.4.11f1',
            'ReleaseVersion': 'OB54',
            'Content-Type': 'application/x-www-form-urlencoded',
            'X-GA': 'v1 1',
            'User-Agent': 'Dalvik/2.1.0 (Linux; U; Android 7.1.2; ASUS_Z01QD Build/QKQ1.190825.002)',
            'Host': 'loginbp.ggpolarbear.com',
            'Connection': 'Keep-Alive',
            'Accept-Encoding': 'gzip'
        }

        conn.request("POST", "/MajorLogin", body=PaYload, headers=headers)
        response = conn.getresponse()
        raw_data = response.read()
        if response.getheader('Content-Encoding') == 'gzip':
            with gzip.GzipFile(fileobj=BytesIO(raw_data)) as f:
                raw_data = f.read()

        if response.status not in [200, 201]:
            print("[-] MajorLogin failed")
            return None

        BesTo_data = json.loads(await DeCode_PackEt(raw_data.hex()))
        JwT_ToKen = BesTo_data['8']['data']
        combined_timestamp, key, iv = await GeT_Key_Iv(raw_data)

        ip, port, ip2, port2 = await GeT_LoGin_PorTs(JwT_ToKen, PaYload)
        if ip is None or port is None or ip2 is None or port2 is None:
            print("[-] Failed to get valid ports")
            return None
        return JwT_ToKen, key, iv, combined_timestamp, ip, port, ip2, port2
    except Exception as e:
        print(f"[-] Token generation error: {e}")
        return None

async def GeT_LoGin_PorTs(JwT_ToKen, PayLoad):
    url = 'https://clientbp.common.ggbluefox.com/GetLoginData'
    headers = {
        'Expect': '100-continue',
        'Authorization': f'Bearer {JwT_ToKen}',
        'X-Unity-Version': '2018.4.11f1',
        'X-GA': 'v1 1',
        'ReleaseVersion': 'OB54',
        'Content-Type': 'application/x-www-form-urlencoded',
        'User-Agent': 'Dalvik/2.1.0 (Linux; U; Android 9; G011A Build/PI)',
        'Host': 'clientbp.common.ggbluefox.com',
        'Connection': 'close',
        'Accept-Encoding': 'gzip, deflate, br',
    }
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, data=PayLoad, ssl=False, timeout=5) as resp:
                if resp.status != 200:
                    return None, None, None, None
                content = await resp.read()
                decoded = await DeCode_PackEt(content.hex())
                if not decoded:
                    return None, None, None, None
                data = json.loads(decoded)
                if '32' not in data or '14' not in data:
                    return None, None, None, None
                address, address2 = data['32']['data'], data['14']['data']
                if not address or not address2:
                    return None, None, None, None
                ip, port = address.rsplit(":", 1)
                ip2, port2 = address2.rsplit(":", 1)
                print(f"[DEBUG] Got ports - Chat: {ip}:{port}, Online: {ip2}:{port2}")
                return ip, int(port), ip2, int(port2)
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
    else: print('Unexpected length'); headers = '0000000'
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

async def SEndPacKeT(OnLinE, ChaT, TypE, PacKeT):
    if TypE == 'ChaT' and ChaT:
        whisper_writer.write(PacKeT)
        await whisper_writer.drain()
    elif TypE == 'OnLine':
        online_writer.write(PacKeT)
        await online_writer.drain()
    else:
        return 'UnsoPorTed TypE !'

async def TcPOnLine(ip, port, key, iv, AutHToKen, reconnect_delay=0.5):
    global online_writer, spam_room, whisper_writer, spammer_uid, spam_chat_id, spam_uid, Spy, Chat_Leave
    while True:
        try:
            reader, writer = await asyncio.open_connection(ip, int(port))
            online_writer = writer
            print(f"[DEBUG] Online connected to {ip}:{port}")
            bytes_payload = bytes.fromhex(AutHToKen)
            online_writer.write(bytes_payload)
            await online_writer.drain()
            while True:
                data2 = await reader.read(9999)
                if not data2: break
                if data2.hex().startswith('0500') and len(data2.hex()) > 1000:
                    try:
                        packet = await DeCode_PackEt(data2.hex()[10:])
                        packet = json.loads(packet)
                        OwNer_UiD, CHaT_CoDe, SQuAD_CoDe = await GeTSQDaTa(packet)
                        JoinCHaT = await AutH_Chat(3, OwNer_UiD, CHaT_CoDe, key, iv)
                        await SEndPacKeT(whisper_writer, online_writer, 'ChaT', JoinCHaT)
                        message = f'[B][C]{await ArA_CoLor()}\n- WeLComE To Emote Bot ! '
                        P = await SEndMsG(0, message, OwNer_UiD, OwNer_UiD, key, iv)
                        await SEndPacKeT(whisper_writer, online_writer, 'ChaT', P)
                    except:
                        pass
            online_writer.close()
            await online_writer.wait_closed()
            online_writer = None
        except Exception as e:
            print(f"- ErroR With {ip}:{port} - {e}")
            online_writer = None
        await asyncio.sleep(reconnect_delay)

async def TcPChaT(ip, port, AutHToKen, key, iv, LoGinDaTaUncRypTinG, ready_event, region, reconnect_delay=0.5):
    global spam_room, whisper_writer, spammer_uid, spam_chat_id, spam_uid, online_writer, Chat_Leave
    while True:
        try:
            reader, writer = await asyncio.open_connection(ip, int(port))
            whisper_writer = writer
            bytes_payload = bytes.fromhex(AutHToKen)
            whisper_writer.write(bytes_payload)
            await whisper_writer.drain()
            ready_event.set()
            print(f"[DEBUG] TcPChaT connected to {ip}:{port}")
            if LoGinDaTaUncRypTinG.Clan_ID:
                clan_id = LoGinDaTaUncRypTinG.Clan_ID
                clan_compiled_data = LoGinDaTaUncRypTinG.Clan_Compiled_Data
                pK = await AuthClan(clan_id, clan_compiled_data, key, iv)
                if whisper_writer:
                    whisper_writer.write(pK)
                    await whisper_writer.drain()
            while True:
                data = await reader.read(9999)
                if not data: break
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
                        # /f command - fast emote
                        if inPuTMsG.strip().startswith('/f'):
                            try:
                                dd = chatdata['5']['data']['16']
                                message = f"[B][C]{await ArA_CoLor()}\n\nOnLy In SQuaD !"
                                P = await SEndMsG(response.Data.chat_type, message, uid, chat_id, key, iv)
                                await SEndPacKeT(whisper_writer, online_writer, 'ChaT', P)
                            except:
                                parts = inPuTMsG.strip().split()
                                message = f'[B][C]{await ArA_CoLor()}\nACITVE TarGeT -> {xMsGFixinG(uid)}\n'
                                P = await SEndMsG(response.Data.chat_type, message, uid, chat_id, key, iv)
                                await SEndPacKeT(whisper_writer, online_writer, 'ChaT', P)
                                uid_list = []
                                idT = None
                                for part in parts[1:]:
                                    try:
                                        uid_list.append(int(part))
                                    except:
                                        try:
                                            idT = int(part)
                                        except:
                                            pass
                                if idT is None:
                                    idT = uid_list.pop() if uid_list else 909000001
                                for i in range(200):
                                    for u in uid_list:
                                        H = await Emote_k(u, idT, key, iv, region)
                                        await SEndPacKeT(whisper_writer, online_writer, 'OnLine', H)
                                    await asyncio.sleep(0.08)

                        # /d command - emote
                        if inPuTMsG.strip().startswith('/d'):
                            try:
                                dd = chatdata['5']['data']['16']
                                message = f"[B][C]{await ArA_CoLor()}\n\nOnLy In SQuaD !"
                                P = await SEndMsG(response.Data.chat_type, message, uid, chat_id, key, iv)
                                await SEndPacKeT(whisper_writer, online_writer, 'ChaT', P)
                            except:
                                parts = inPuTMsG.strip().split()
                                message = f'[B][C]{await ArA_CoLor()}\nACITVE TarGeT -> {xMsGFixinG(uid)}\n'
                                P = await SEndMsG(response.Data.chat_type, message, uid, chat_id, key, iv)
                                await SEndPacKeT(whisper_writer, online_writer, 'ChaT', P)
                                uid_list = []
                                idT = None
                                for part in parts[1:]:
                                    try:
                                        uid_list.append(int(part))
                                    except:
                                        try:
                                            idT = int(part)
                                        except:
                                            pass
                                if idT is None:
                                    idT = uid_list.pop() if uid_list else 909000001
                                for u in uid_list:
                                    H = await Emote_k(u, idT, key, iv, region)
                                    await SEndPacKeT(whisper_writer, online_writer, 'OnLine', H)

                        # /s command - open squad
                        if inPuTMsG.strip().startswith('/s'):
                            EM = await FS(key, iv)
                            await SEndPacKeT(whisper_writer, online_writer, 'OnLine', EM)

                        # /x/ command - join squad by code
                        if inPuTMsG.startswith('/x/'):
                            CodE = inPuTMsG.split('/x/')[1]
                            try:
                                dd = chatdata['5']['data']['16']
                                EM = await GenJoinSquadsPacket(CodE, key, iv)
                                await SEndPacKeT(whisper_writer, online_writer, 'OnLine', EM)
                            except:
                                pass

                        # leave command
                        if inPuTMsG == 'leave':
                            leave = await ExiT(BOT_UID, key, iv)
                            await SEndPacKeT(whisper_writer, online_writer, 'OnLine', leave)

                        # /5 command - invite to squad
                        if inPuTMsG.startswith(("/5")):
                            try:
                                dd = chatdata['5']['data']['16']
                                message = f"[B][C]{await ArA_CoLor()}\n\nAccepT My InV FasT"
                                P = await SEndMsG(response.Data.chat_type, message, uid, chat_id, key, iv)
                                await SEndPacKeT(whisper_writer, online_writer, 'ChaT', P)
                                PAc = await OpEnSq(key, iv, region)
                                await SEndPacKeT(whisper_writer, online_writer, 'OnLine', PAc)
                                C = await cHSq(5, uid, key, iv, region)
                                await asyncio.sleep(0.5)
                                await SEndPacKeT(whisper_writer, online_writer, 'OnLine', C)
                                V = await SEnd_InV(5, uid, key, iv, region)
                                await asyncio.sleep(0.5)
                                await SEndPacKeT(whisper_writer, online_writer, 'OnLine', V)
                                E = await ExiT(BOT_UID, key, iv)
                                await asyncio.sleep(3)
                                await SEndPacKeT(whisper_writer, online_writer, 'OnLine', E)
                            except:
                                pass

                        # help command
                        if inPuTMsG in ("dev", "help"):
                            message = '/d <uid1> <uid2>... <emoteid> /f <uid1> <uid2>... <emoteid> for fast emote'
                            P = await SEndMsG(response.Data.chat_type, message, uid, chat_id, key, iv)
                            await SEndPacKeT(whisper_writer, online_writer, 'ChaT', P)
                        response = None

            whisper_writer.close()
            await whisper_writer.wait_closed()
            whisper_writer = None
        except Exception as e:
            print(f"ErroR {ip}:{port} - {e}")
            whisper_writer = None
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
async def perform_emote(team_code: str, uids: list, emote_id: int):
    global key, iv, region, online_writer, BOT_UID
    if online_writer is None:
        raise Exception("Bot not connected")
    try:
        EM = await GenJoinSquadsPacket(team_code, key, iv)
        await SEndPacKeT(None, online_writer, 'OnLine', EM)
        await asyncio.sleep(1.0)
        for uid_str in uids:
            uid = int(uid_str)
            H = await Emote_k(uid, emote_id, key, iv, region)
            await SEndPacKeT(None, online_writer, 'OnLine', H)
        await asyncio.sleep(0.5)
        LV = await ExiT(BOT_UID, key, iv)
        await SEndPacKeT(None, online_writer, 'OnLine', LV)
        return {"status": "success", "message": "Emote done in one click"}
    except Exception as e:
        raise Exception(f"Failed to perform emote: {str(e)}")

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

    try:
        emote_id = int(emote_id_str)
    except:
        return jsonify({"status": "error", "message": "emote_id must be integer"})

    uids = [uid for uid in [uid1, uid2, uid3, uid4, uid5, uid6] if uid]

    if not uids:
        return jsonify({"status": "error", "message": "Provide at least one UID"})

    asyncio.run_coroutine_threadsafe(
        perform_emote(team_code, uids, emote_id), loop
    )

    return jsonify({
        "status": "success",
        "team_code": team_code,
        "uids": uids,
        "emote_id": emote_id_str,
        "message": "Emote triggered"
    })

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port, debug=False, use_reloader=False)

# ========== MAIN BOT ==========
async def MaiiiinE():
    global loop, key, iv, region, BOT_UID, online_writer, whisper_writer

    Uid, Pw = '6383837566', 'pak_caRYTA'

    Access_ToKen, Access_Uid = await Guest_GeneRaTe(Uid, Pw)
    if not Access_ToKen or not Access_Uid:
        print("ErroR - InvaLid AccounT")
        return None

    token_res = await ToKen_GeneRaTe(Access_ToKen, Access_Uid)
    if not token_res:
        print("TarGeT AccounT => BannEd / NoT ReGisTeReD !")
        return None

    JwT_ToKen, key, iv, timestamp, ip, port, ip2, port2 = token_res

    # Decode JWT to get account UID
    try:
        AfTer_DeC_JwT = jwt.decode(JwT_ToKen, options={"verify_signature": False})
        TarGeT = AfTer_DeC_JwT.get('account_id')
    except:
        TarGeT = BOT_UID

    region = 'ind'  # Default region, will be updated from GetLoginData

    loop = asyncio.get_running_loop()

    # Get Login Data for ports
    PayLoad = (await CrEaTe_ProTo({
        3: str(datetime.now())[:-7],
        4: "free fire",
        5: 2,
        7: '1.126.2',
        8: "Android OS 11 / API-30 (RQ3A.210805.001)",
        9: "Handheld",
        10: "Verizon",
        11: "WIFI",
        12: 1080,
        13: 2400,
        14: "440",
        15: "ARMv8",
        16: 6144,
        17: "Adreno (TM) 650",
        18: "OpenGL ES 3.2 V@1.50",
        19: "Google|34a7dcdf-a7d5-4cb6-8d7e-3b0e448a0c57",
        20: "",
        21: "en",
        22: Access_Uid,
        23: "4",
        24: "Handheld",
        25: "google G011A",
        29: Access_ToKen,
        30: 3,
        41: "Verizon",
        42: "WIFI",
        57: "1ac4b80ecf0478a44203bf8fac6120f5",
        60: 32966,
        61: 29779,
        62: 2479,
        63: 914,
        64: 31176,
        65: 32966,
        66: 31176,
        67: 32966,
        70: 4,
        73: 2,
        74: "/data/app/com.dts.freefireth-g8eDE0T268FtFmnFZ2UpmA==/lib/arm",
        76: 1,
        77: "5b892aaabd688e571f688053118a162b|/data/app/com.dts.freefireth-g8eDE0T268FtFmnFZ2UpmA==/base.apk",
        78: 6,
        79: 1,
        81: "64",
        83: '2024010012',
        86: "OpenGLES3",
        87: 255,
        88: "4",
        89: "J\x03FD\x04\r_UH\x03\x0b\x16_\x03D^J>\x0fWT\x00\\=\nQ_;\x00\r;Z\x05a",
        90: "Phoenix",
        91: "AZ",
        92: 10214,
        93: "3rd_party",
        94: "KqsHT7gtKWkK0gY/HwmdwXIhSiz4fQldX3YjZeK86XBTthKAf1bW4Vsz6Di0S8vqr0Jc4HX3TMQ8KaUU3GeVvYzWF9I=",
        95: 111207,
        97: 1,
        98: 1,
        99: "4",
        100: "4"
    })).hex()
    PayLoad = bytes.fromhex(await EnC_AEs(PayLoad))

    LoGinDaTa = await GeT_LoGin_PorTs(JwT_ToKen, PayLoad)
    if not LoGinDaTa or LoGinDaTa[0] is None:
        print("ErroR - GeTinG PorTs From LoGin DaTa !")
        return None

    ChaTiP, ChaTporT, OnLineiP, OnLineporT = LoGinDaTa

    # Update region from login response
    try:
        url = 'https://clientbp.common.ggbluefox.com/GetLoginData'
        headers = {'Authorization': f'Bearer {JwT_ToKen}'}
        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, data=PayLoad, ssl=False, timeout=5) as resp:
                if resp.status == 200:
                    content = await resp.read()
                    decoded = await DeCode_PackEt(content.hex())
                    if decoded:
                        data = json.loads(decoded)
                        if '3' in data:
                            region = data['3']['data'].lower()
    except:
        pass

    AutHToKen = await xAuThSTarTuP(int(TarGeT), JwT_ToKen, int(timestamp), key, iv)
    ready_event = asyncio.Event()

    # Create a dummy LoginData object
    class DummyLoginData:
        pass
    LoGinDaTaUncRypTinG = DummyLoginData()
    LoGinDaTaUncRypTinG.Clan_ID = None
    LoGinDaTaUncRypTinG.Clan_Compiled_Data = None

    task1 = asyncio.create_task(
        TcPChaT(ChaTiP, ChaTporT, AutHToKen, key, iv,
                LoGinDaTaUncRypTinG, ready_event, region)
    )

    await ready_event.wait()
    print("[DEBUG] Chat connection established!")
    await asyncio.sleep(1)
    print("[DEBUG] Starting Online connection...")

    task2 = asyncio.create_task(
        TcPOnLine(OnLineiP, OnLineporT, key, iv, AutHToKen)
    )

    #os.system('clear')
    print(f"\n - BoT STarTinG And OnLine on TarGet : {TarGeT}")
    print(" - BoT sTaTus > GooD | OnLinE ! (: \n")

    flask_thread = threading.Thread(target=run_flask, daemon=True)
    flask_thread.start()

    await asyncio.gather(task1, task2)

async def StarTinG():
    while True:
        try:
            await asyncio.wait_for(MaiiiinE(), timeout=7 * 60 * 60)
        except asyncio.TimeoutError:
            print("Token ExpiRed ! , ResTartinG")
        except Exception as e:
            print(f"ErroR TcP - {e} => ResTarTinG ...")

if __name__ == '__main__':
    asyncio.run(StarTinG())