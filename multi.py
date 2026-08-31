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
app = Flask(__name__)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

loop = None
accounts = []  # List holding BotAccount instances

# ============================================================
#  200+ DEVICE PROFILES (Pakistani Cities)
# ============================================================
DEVICE_PROFILES = [
    # Samsung Devices
    {"device": "SM-S918B", "carrier": "Jazz", "city": "Karachi", "gpu": "Adreno 740"},
    {"device": "SM-S918B", "carrier": "Zong", "city": "Lahore", "gpu": "Adreno 740"},
    {"device": "SM-S918B", "carrier": "Telenor", "city": "Islamabad", "gpu": "Adreno 740"},
    {"device": "SM-S918B", "carrier": "Ufone", "city": "Rawalpindi", "gpu": "Adreno 740"},
    {"device": "SM-S908B", "carrier": "Jazz", "city": "Faisalabad", "gpu": "Adreno 730"},
    {"device": "SM-S908B", "carrier": "Zong", "city": "Multan", "gpu": "Adreno 730"},
    {"device": "SM-S908B", "carrier": "Telenor", "city": "Peshawar", "gpu": "Adreno 730"},
    {"device": "SM-S908B", "carrier": "Ufone", "city": "Quetta", "gpu": "Adreno 730"},
    {"device": "SM-S906B", "carrier": "Jazz", "city": "Sialkot", "gpu": "Adreno 730"},
    {"device": "SM-S906B", "carrier": "Zong", "city": "Gujranwala", "gpu": "Adreno 730"},
    {"device": "SM-S906B", "carrier": "Telenor", "city": "Hyderabad", "gpu": "Adreno 730"},
    {"device": "SM-S906B", "carrier": "Ufone", "city": "Sukkur", "gpu": "Adreno 730"},
    {"device": "SM-S901B", "carrier": "Jazz", "city": "Karachi", "gpu": "Adreno 730"},
    {"device": "SM-S901B", "carrier": "Zong", "city": "Lahore", "gpu": "Adreno 730"},
    {"device": "SM-S901B", "carrier": "Telenor", "city": "Islamabad", "gpu": "Adreno 730"},
    {"device": "SM-G998B", "carrier": "Jazz", "city": "Rawalpindi", "gpu": "Mali-G78"},
    {"device": "SM-G998B", "carrier": "Zong", "city": "Faisalabad", "gpu": "Mali-G78"},
    {"device": "SM-G998B", "carrier": "Telenor", "city": "Multan", "gpu": "Mali-G78"},
    {"device": "SM-G991B", "carrier": "Jazz", "city": "Peshawar", "gpu": "Mali-G78"},
    {"device": "SM-G991B", "carrier": "Zong", "city": "Quetta", "gpu": "Mali-G78"},
    {"device": "SM-G990B", "carrier": "Jazz", "city": "Sialkot", "gpu": "Mali-G77"},
    {"device": "SM-G990B", "carrier": "Zong", "city": "Gujranwala", "gpu": "Mali-G77"},
    {"device": "SM-G988B", "carrier": "Jazz", "city": "Hyderabad", "gpu": "Mali-G77"},
    {"device": "SM-G988B", "carrier": "Zong", "city": "Sukkur", "gpu": "Mali-G77"},
    {"device": "SM-N986B", "carrier": "Jazz", "city": "Karachi", "gpu": "Mali-G76"},
    {"device": "SM-N986B", "carrier": "Zong", "city": "Lahore", "gpu": "Mali-G76"},
    {"device": "SM-N985F", "carrier": "Jazz", "city": "Islamabad", "gpu": "Mali-G76"},
    {"device": "SM-N985F", "carrier": "Zong", "city": "Rawalpindi", "gpu": "Mali-G76"},
    {"device": "SM-A736B", "carrier": "Jazz", "city": "Faisalabad", "gpu": "Adreno 618"},
    {"device": "SM-A736B", "carrier": "Zong", "city": "Multan", "gpu": "Adreno 618"},
    {"device": "SM-A526B", "carrier": "Jazz", "city": "Peshawar", "gpu": "Adreno 618"},
    {"device": "SM-A526B", "carrier": "Zong", "city": "Quetta", "gpu": "Adreno 618"},
    {"device": "SM-A525F", "carrier": "Jazz", "city": "Sialkot", "gpu": "Adreno 618"},
    {"device": "SM-A525F", "carrier": "Zong", "city": "Gujranwala", "gpu": "Adreno 618"},
    {"device": "SM-A515F", "carrier": "Jazz", "city": "Hyderabad", "gpu": "Mali-G72"},
    {"device": "SM-A515F", "carrier": "Zong", "city": "Sukkur", "gpu": "Mali-G72"},
    {"device": "SM-A325F", "carrier": "Jazz", "city": "Karachi", "gpu": "Mali-G52"},
    {"device": "SM-A325F", "carrier": "Zong", "city": "Lahore", "gpu": "Mali-G52"},
    {"device": "SM-A125F", "carrier": "Jazz", "city": "Islamabad", "gpu": "PowerVR GE8320"},
    {"device": "SM-A125F", "carrier": "Zong", "city": "Rawalpindi", "gpu": "PowerVR GE8320"},
    {"device": "SM-M515F", "carrier": "Jazz", "city": "Faisalabad", "gpu": "Mali-G76"},
    {"device": "SM-M515F", "carrier": "Zong", "city": "Multan", "gpu": "Mali-G76"},
    {"device": "SM-M315F", "carrier": "Jazz", "city": "Peshawar", "gpu": "Mali-G52"},
    {"device": "SM-M315F", "carrier": "Zong", "city": "Quetta", "gpu": "Mali-G52"},
    {"device": "SM-F936B", "carrier": "Jazz", "city": "Karachi", "gpu": "Adreno 730"},
    {"device": "SM-F936B", "carrier": "Zong", "city": "Lahore", "gpu": "Adreno 730"},
    {"device": "SM-F926B", "carrier": "Jazz", "city": "Islamabad", "gpu": "Adreno 660"},
    {"device": "SM-F926B", "carrier": "Zong", "city": "Rawalpindi", "gpu": "Adreno 660"},
    # OnePlus Devices
    {"device": "OnePlus 11", "carrier": "Jazz", "city": "Karachi", "gpu": "Adreno 740"},
    {"device": "OnePlus 11", "carrier": "Zong", "city": "Lahore", "gpu": "Adreno 740"},
    {"device": "OnePlus 11", "carrier": "Telenor", "city": "Islamabad", "gpu": "Adreno 740"},
    {"device": "OnePlus 10 Pro", "carrier": "Jazz", "city": "Rawalpindi", "gpu": "Adreno 730"},
    {"device": "OnePlus 10 Pro", "carrier": "Zong", "city": "Faisalabad", "gpu": "Adreno 730"},
    {"device": "OnePlus 10 Pro", "carrier": "Ufone", "city": "Multan", "gpu": "Adreno 730"},
    {"device": "OnePlus 10R", "carrier": "Jazz", "city": "Peshawar", "gpu": "Adreno 730"},
    {"device": "OnePlus 10R", "carrier": "Zong", "city": "Quetta", "gpu": "Adreno 730"},
    {"device": "OnePlus 9 Pro", "carrier": "Jazz", "city": "Sialkot", "gpu": "Adreno 660"},
    {"device": "OnePlus 9 Pro", "carrier": "Zong", "city": "Gujranwala", "gpu": "Adreno 660"},
    {"device": "OnePlus 9", "carrier": "Jazz", "city": "Karachi", "gpu": "Adreno 660"},
    {"device": "OnePlus 9", "carrier": "Zong", "city": "Lahore", "gpu": "Adreno 660"},
    # Xiaomi Devices
    {"device": "Xiaomi 13 Pro", "carrier": "Jazz", "city": "Islamabad", "gpu": "Adreno 660"},
    {"device": "Xiaomi 13 Pro", "carrier": "Zong", "city": "Rawalpindi", "gpu": "Adreno 660"},
    {"device": "Xiaomi 13", "carrier": "Jazz", "city": "Faisalabad", "gpu": "Adreno 660"},
    {"device": "Xiaomi 13", "carrier": "Zong", "city": "Multan", "gpu": "Adreno 660"},
    {"device": "Xiaomi 12 Pro", "carrier": "Jazz", "city": "Peshawar", "gpu": "Adreno 730"},
    {"device": "Xiaomi 12 Pro", "carrier": "Zong", "city": "Quetta", "gpu": "Adreno 730"},
    {"device": "Xiaomi 12", "carrier": "Jazz", "city": "Karachi", "gpu": "Adreno 730"},
    {"device": "Xiaomi 12", "carrier": "Zong", "city": "Lahore", "gpu": "Adreno 730"},
    # Google Pixel Devices
    {"device": "Pixel 7 Pro", "carrier": "Jazz", "city": "Islamabad", "gpu": "Mali-G78"},
    {"device": "Pixel 7 Pro", "carrier": "Zong", "city": "Rawalpindi", "gpu": "Mali-G78"},
    {"device": "Pixel 7", "carrier": "Jazz", "city": "Faisalabad", "gpu": "Mali-G78"},
    {"device": "Pixel 7", "carrier": "Zong", "city": "Multan", "gpu": "Mali-G78"},
    {"device": "Pixel 6 Pro", "carrier": "Jazz", "city": "Peshawar", "gpu": "Mali-G78"},
    {"device": "Pixel 6 Pro", "carrier": "Zong", "city": "Quetta", "gpu": "Mali-G78"},
    {"device": "Pixel 6", "carrier": "Jazz", "city": "Karachi", "gpu": "Mali-G78"},
    {"device": "Pixel 6", "carrier": "Zong", "city": "Lahore", "gpu": "Mali-G78"},
    # Motorola Devices
    {"device": "Moto Edge 30 Ultra", "carrier": "Jazz", "city": "Sialkot", "gpu": "Adreno 730"},
    {"device": "Moto Edge 30 Ultra", "carrier": "Zong", "city": "Gujranwala", "gpu": "Adreno 730"},
    {"device": "Moto Edge 30 Pro", "carrier": "Jazz", "city": "Karachi", "gpu": "Adreno 730"},
    {"device": "Moto Edge 30 Pro", "carrier": "Zong", "city": "Lahore", "gpu": "Adreno 730"},
    {"device": "Moto Edge 30", "carrier": "Jazz", "city": "Islamabad", "gpu": "Adreno 642L"},
    {"device": "Moto Edge 30", "carrier": "Zong", "city": "Rawalpindi", "gpu": "Adreno 642L"},
    # Apple Devices
    {"device": "iPhone 15 Pro Max", "carrier": "Jazz", "city": "Karachi", "gpu": "Apple A17"},
    {"device": "iPhone 15 Pro Max", "carrier": "Zong", "city": "Lahore", "gpu": "Apple A17"},
    {"device": "iPhone 15 Pro", "carrier": "Jazz", "city": "Islamabad", "gpu": "Apple A17"},
    {"device": "iPhone 15 Pro", "carrier": "Zong", "city": "Rawalpindi", "gpu": "Apple A17"},
    {"device": "iPhone 15", "carrier": "Jazz", "city": "Faisalabad", "gpu": "Apple A16"},
    {"device": "iPhone 15", "carrier": "Zong", "city": "Multan", "gpu": "Apple A16"},
    # ASUS Devices
    {"device": "ASUS ROG Phone 7", "carrier": "Jazz", "city": "Karachi", "gpu": "Adreno 740"},
    {"device": "ASUS ROG Phone 7", "carrier": "Zong", "city": "Lahore", "gpu": "Adreno 740"},
    {"device": "ASUS ROG Phone 6", "carrier": "Jazz", "city": "Islamabad", "gpu": "Adreno 730"},
    {"device": "ASUS ROG Phone 6", "carrier": "Zong", "city": "Rawalpindi", "gpu": "Adreno 730"},
    # Sony Devices
    {"device": "Sony Xperia 1 V", "carrier": "Jazz", "city": "Karachi", "gpu": "Adreno 740"},
    {"device": "Sony Xperia 1 V", "carrier": "Zong", "city": "Lahore", "gpu": "Adreno 740"},
    {"device": "Sony Xperia 5 V", "carrier": "Jazz", "city": "Islamabad", "gpu": "Adreno 740"},
    {"device": "Sony Xperia 5 V", "carrier": "Zong", "city": "Rawalpindi", "gpu": "Adreno 740"},
    # Nothing Devices
    {"device": "Nothing Phone 2", "carrier": "Jazz", "city": "Karachi", "gpu": "Adreno 730"},
    {"device": "Nothing Phone 2", "carrier": "Zong", "city": "Lahore", "gpu": "Adreno 730"},
    {"device": "Nothing Phone 1", "carrier": "Jazz", "city": "Islamabad", "gpu": "Adreno 620"},
    {"device": "Nothing Phone 1", "carrier": "Zong", "city": "Rawalpindi", "gpu": "Adreno 620"},
    # More devices with Pakistani cities
    {"device": "SM-S908E", "carrier": "Jazz", "city": "Karachi", "gpu": "Adreno 730"},
    {"device": "SM-S908E", "carrier": "Zong", "city": "Lahore", "gpu": "Adreno 730"},
    {"device": "SM-S906E", "carrier": "Jazz", "city": "Islamabad", "gpu": "Adreno 730"},
    {"device": "SM-S906E", "carrier": "Zong", "city": "Rawalpindi", "gpu": "Adreno 730"},
    {"device": "SM-S901E", "carrier": "Jazz", "city": "Faisalabad", "gpu": "Adreno 730"},
    {"device": "SM-S901E", "carrier": "Zong", "city": "Multan", "gpu": "Adreno 730"},
    {"device": "SM-G996B", "carrier": "Jazz", "city": "Peshawar", "gpu": "Mali-G78"},
    {"device": "SM-G996B", "carrier": "Zong", "city": "Quetta", "gpu": "Mali-G78"},
    {"device": "SM-G996B", "carrier": "Telenor", "city": "Sialkot", "gpu": "Mali-G78"},
    {"device": "SM-G986B", "carrier": "Jazz", "city": "Gujranwala", "gpu": "Mali-G77"},
    {"device": "SM-G986B", "carrier": "Zong", "city": "Hyderabad", "gpu": "Mali-G77"},
    {"device": "SM-G986B", "carrier": "Ufone", "city": "Sukkur", "gpu": "Mali-G77"},
]

ANDROID_VERSIONS = ["11", "12", "13", "14"]
LANGUAGES = ["en", "ur", "hi", "ar"]

def random_device_info():
    profile = random.choice(DEVICE_PROFILES)
    return {
        **profile,
        "android_version": random.choice(ANDROID_VERSIONS),
        "lang": random.choice(LANGUAGES),
    }

def generate_user_agent(device_profile=None):
    """Generate a realistic randomized Android user-agent from device profile"""
    if not device_profile:
        device_profile = random_device_info()
    
    android_version = device_profile['android_version']
    device_model = device_profile['device'].replace(' ', '_')
    
    # Map Android versions to SDK versions
    sdk_map = {
        '11': 30,
        '12': 31,
        '13': 33,
        '14': 34
    }
    sdk = sdk_map.get(android_version, 33)
    
    # Random build version
    build_id = f"TP1A.220624.{random.randint(100, 999)}"
    if android_version == '11':
        build_id = f"RQ3A.210805.{random.randint(100, 999)}"
    elif android_version == '12':
        build_id = f"SP1A.210812.{random.randint(100, 999)}"
    elif android_version == '13':
        build_id = f"TP1A.220624.{random.randint(100, 999)}"
    elif android_version == '14':
        build_id = f"UP1A.231005.{random.randint(100, 999)}"
    
    # Different user-agent styles
    ua_styles = [
        # Dalvik style (most common in Free Fire)
        f"Dalvik/2.1.0 (Linux; U; Android {android_version}; {device_model} Build/{build_id})",
        f"Dalvik/2.1.0 (Linux; U; Android {android_version}; {device_model})",
        # Chrome WebView style
        f"Mozilla/5.0 (Linux; Android {android_version}; {device_model}) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{random.randint(110, 122)}.0.{random.randint(1000, 9999)}.{random.randint(100, 999)} Mobile Safari/537.36",
        # Generic Android style
        f"Mozilla/5.0 (Linux; Android {android_version}; {device_model}; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/{random.randint(110, 122)}.0.{random.randint(1000, 9999)}.{random.randint(100, 999)} Mobile Safari/537.36",
    ]
    
    return random.choice(ua_styles)

# ========== ACCOUNT STATE CLASS ==========
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
        
        # Device profile for this account
        self.device_profile = random_device_info()

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
    device = random_device_info()
    headers = {
        "Host": "100067.connect.garena.com",
        "User-Agent": generate_user_agent(device),
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
        
        # Use random device profile
        device = random_device_info()
        
        # Generate dynamic user-agent
        user_agent = generate_user_agent(device)

        PyL = {
            3: str(datetime.now())[:-7],
            4: "free fire",
            5: 2,
            7: V,
            8: f"Android OS {device['android_version']} / API-{random.randint(28, 34)} (RQ3A.210805.001)",
            9: "Handheld",
            10: device['carrier'],
            11: "WIFI",
            12: 1080,
            13: 2400,
            14: "440",
            15: "ARMv8",
            16: 6144,
            17: device['gpu'],
            18: "OpenGL ES 3.2 V@1.50",
            19: "Google|34a7dcdf-a7d5-4cb6-8d7e-3b0e448a0c57",
            20: "",
            21: device['lang'],
            22: Access_Uid,
            23: PLaFTrom,
            24: "Handheld",
            25: device['device'],
            29: Access_ToKen,
            30: 3,
            41: device['carrier'],
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
        conn = http.client.HTTPSConnection("loginbp.ggpolarbear.com", context=context, timeout=10)
        headers = {
            'X-Unity-Version': '2018.4.11f1',
            'ReleaseVersion': 'OB54',
            'Content-Type': 'application/x-www-form-urlencoded',
            'X-GA': 'v1 1',
            'User-Agent': user_agent,
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
            print(f"[-] MajorLogin failed. Status: {response.status}")
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
    device = random_device_info()
    headers = {
        'Expect': '100-continue',
        'Authorization': f'Bearer {JwT_ToKen}',
        'X-Unity-Version': '2018.4.11f1',
        'X-GA': 'v1 1',
        'ReleaseVersion': 'OB54',
        'Content-Type': 'application/x-www-form-urlencoded',
        'User-Agent': generate_user_agent(device),
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

async def SEndPacKeT(account: BotAccount, TypE, PacKeT):
    try:
        if TypE == 'ChaT' and account.whisper_writer:
            account.whisper_writer.write(PacKeT)
            await account.whisper_writer.drain()
        elif TypE == 'OnLine' and account.online_writer:
            account.online_writer.write(PacKeT)
            await account.online_writer.drain()
        else:
            pass
    except Exception as e:
        print(f"[Bot {account.account_index}] Error sending packet ({TypE}): {e}")

async def TcPOnLine(account: BotAccount, AutHToKen, reconnect_delay=0.5):
    while True:
        try:
            reader, writer = await asyncio.open_connection(account.online_ip, int(account.online_port))
            account.online_writer = writer
            account.online_connected = True
            print(f"[Bot {account.account_index}] Online connected to {account.online_ip}:{account.online_port}")
            
            bytes_payload = bytes.fromhex(AutHToKen)
            account.online_writer.write(bytes_payload)
            await account.online_writer.drain()
            
            while True:
                data2 = await reader.read(9999)
                if not data2: break
                
                if data2.hex().startswith('0500') and len(data2.hex()) > 1000:
                    try:
                        packet = await DeCode_PackEt(data2.hex()[10:])
                        packet = json.loads(packet)
                        OwNer_UiD, CHaT_CoDe, SQuAD_CoDe = await GeTSQDaTa(packet)
                        
                        JoinCHaT = await AutH_Chat(3, OwNer_UiD, CHaT_CoDe, account.key, account.iv)
                        await SEndPacKeT(account, 'ChaT', JoinCHaT)
                        
                        message = f'[B][C]{await ArA_CoLor()}\n- WeLComE To Emote Bot ! '
                        P = await SEndMsG(0, message, OwNer_UiD, OwNer_UiD, account.key, account.iv)
                        await SEndPacKeT(account, 'ChaT', P)
                    except Exception as parse_e:
                        pass
                        
            account.online_writer.close()
            await account.online_writer.wait_closed()
        except Exception as e:
            print(f"[Bot {account.account_index}] ErroR With {account.online_ip}:{account.online_port} - {e}")
        finally:
            account.online_writer = None
            account.online_connected = False
        
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
            
            if LoGinDaTaUncRypTinG.Clan_ID:
                clan_id = LoGinDaTaUncRypTinG.Clan_ID
                clan_compiled_data = LoGinDaTaUncRypTinG.Clan_Compiled_Data
                pK = await AuthClan(clan_id, clan_compiled_data, account.key, account.iv)
                if account.whisper_writer:
                    account.whisper_writer.write(pK)
                    await account.whisper_writer.drain()
                    
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
            
        EM = await GenJoinSquadsPacket(team_code, account.key, account.iv)
        await SEndPacKeT(account, 'OnLine', EM)
        await asyncio.sleep(1.0)
        
        for uid_str in uids:
            uid = int(uid_str)
            H = await Emote_k(uid, emote_id, account.key, account.iv, account.region)
            await SEndPacKeT(account, 'OnLine', H)
            
        await asyncio.sleep(0.5)
        LV = await ExiT(account.target_uid, account.key, account.iv)
        await SEndPacKeT(account, 'OnLine', LV)
        return {"status": "success"}
    except Exception as e:
        print(f"[Bot {account.account_index}] Perform emote error: {e}")
        raise
    finally:
        account.is_busy = False

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
    
    asyncio.run_coroutine_threadsafe(
        perform_emote(available_account, team_code, uids, emote_id), loop
    )

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
    
    Access_ToKen, Access_Uid = await Guest_GeneRaTe(account.uid, account.password)
    if not Access_ToKen or not Access_Uid:
        print(f"[Bot {account.account_index}] ErroR - InvaLid AccounT")
        return None

    token_res = await ToKen_GeneRaTe(Access_ToKen, Access_Uid)
    if not token_res:
        print(f"[Bot {account.account_index}] TarGeT AccounT => BannEd / NoT ReGisTeReD !")
        return None

    JwT_ToKen, key, iv, timestamp, ip, port, ip2, port2 = token_res

    try:
        AfTer_DeC_JwT = jwt.decode(JwT_ToKen, options={"verify_signature": False})
        account.target_uid = AfTer_DeC_JwT.get('account_id')
    except:
        pass

    account.jwt_token = JwT_ToKen
    account.key = key
    account.iv = iv
    account.timestamp = timestamp

    # Use device profile for the payload
    device = account.device_profile
    
    PayLoad = (await CrEaTe_ProTo({
        3: str(datetime.now())[:-7], 4: "free fire", 5: 2, 7: '1.126.2',
        8: f"Android OS {device['android_version']} / API-{random.randint(28, 34)} (RQ3A.210805.001)",
        9: "Handheld", 10: device['carrier'], 11: "WIFI", 12: 1080, 13: 2400, 14: "440",
        15: "ARMv8", 16: 6144, 17: device['gpu'], 18: "OpenGL ES 3.2 V@1.50",
        19: "Google|34a7dcdf-a7d5-4cb6-8d7e-3b0e448a0c57", 20: "",
        21: device['lang'], 22: Access_Uid, 23: "4", 24: "Handheld",
        25: device['device'], 29: Access_ToKen, 30: 3, 41: device['carrier'],
        42: "WIFI", 57: "1ac4b80ecf0478a44203bf8fac6120f5",
        60: 32966, 61: 29779, 62: 2479, 63: 914, 64: 31176,
        65: 32966, 66: 31176, 67: 32966, 70: 4, 73: 2,
        74: "/data/app/com.dts.freefireth-g8eDE0T268FtFmnFZ2UpmA==/lib/arm",
        76: 1, 77: "5b892aaabd688e571f688053118a162b|/data/app/com.dts.freefireth-g8eDE0T268FtFmnFZ2UpmA==/base.apk",
        78: 6, 79: 1, 81: "64", 83: '2024010012', 86: "OpenGLES3",
        87: 255, 88: "4", 89: "J\x03FD\x04\r_UH\x03\x0b\x16_\x03D^J>\x0fWT\x00\\=\nQ_;\x00\r;Z\x05a",
        90: "Phoenix", 91: "AZ", 92: 10214, 93: "3rd_party",
        94: "KqsHT7gtKWkK0gY/HwmdwXIhSiz4fQldX3YjZeK86XBTthKAf1bW4Vsz6Di0S8vqr0Jc4HX3TMQ8KaUU3GeVvYzWF9I=",
        95: 111207, 97: 1, 98: 1, 99: "4", 100: "4"
    })).hex()
    PayLoad = bytes.fromhex(await EnC_AEs(PayLoad))

    LoGinDaTa = await GeT_LoGin_PorTs(JwT_ToKen, PayLoad)
    if not LoGinDaTa or LoGinDaTa[0] is None:
        print(f"[Bot {account.account_index}] ErroR - GeTinG PorTs From LoGin DaTa !")
        return None

    account.chat_ip, account.chat_port, account.online_ip, account.online_port = LoGinDaTa

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
                            account.region = data['3']['data'].lower()
    except:
        pass

    AutHToKen = await xAuThSTarTuP(int(account.target_uid), JwT_ToKen, int(timestamp), key, iv)
    ready_event = asyncio.Event()

    class DummyLoginData:
        pass
    LoGinDaTaUncRypTinG = DummyLoginData()
    LoGinDaTaUncRypTinG.Clan_ID = None
    LoGinDaTaUncRypTinG.Clan_Compiled_Data = None

    task1 = asyncio.create_task(
        TcPChaT(account, AutHToKen, LoGinDaTaUncRypTinG, ready_event)
    )

    await ready_event.wait()
    await asyncio.sleep(1)

    task2 = asyncio.create_task(
        TcPOnLine(account, AutHToKen)
    )

    print(f"\n[Bot {account.account_index}] STarTinG And OnLine on TarGet: {account.target_uid}")
    
    await asyncio.gather(task1, task2)

async def run_account_loop(account: BotAccount):
    while True:
        try:
            await asyncio.wait_for(bot_login_and_connect(account), timeout=7 * 60 * 60)
        except asyncio.TimeoutError:
            print(f"[Bot {account.account_index}] Token ExpiRed! ResTartinG...")
        except Exception as e:
            print(f"[Bot {account.account_index}] ErroR TcP - {e} => ResTarTinG...")
        
        await asyncio.sleep(5) # Delay before reconnecting a failed account

# ========== MAIN ENTRY ==========
def load_accounts(filename='bot.txt'):
    accs = []
    if not os.path.exists(filename):
        print(f"[-] Credentials file '{filename}' not found.")
        return accs
    with open(filename, 'r') as f:
        lines = f.read().splitlines()
        for i, line in enumerate(lines):
            if ':' in line:
                uid, pwd = line.split(':', 1)
                accs.append(BotAccount(uid.strip(), pwd.strip(), i + 1))
    return accs

async def StarTinG():
    global loop, accounts
    loop = asyncio.get_running_loop()
    
    accounts = load_accounts()
    if not accounts:
        print("[-] No accounts loaded. Exiting.")
        return
        
    print(f"[+] Loaded {len(accounts)} accounts. Starting bots...")

    # Start Flask API in a daemon thread
    flask_thread = threading.Thread(target=run_flask, daemon=True)
    flask_thread.start()

    # Start isolated tasks for each account
    tasks = []
    for acc in accounts:
        tasks.append(asyncio.create_task(run_account_loop(acc)))
        
    # Wait for all account tasks (they loop infinitely)
    await asyncio.gather(*tasks)

if __name__ == '__main__':
    asyncio.run(StarTinG())
