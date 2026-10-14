# -*- coding: utf-8 -*-
"""
IdeaVault - Modern RTL Dashboard
Single-file desktop launcher.

این فایل رابط کاربری HTML آپلودشده را بدون نیاز به فایل HTML جداگانه اجرا می‌کند.
"""

import base64
import hashlib
import hmac
import html
import json
import os
import re
import secrets
import smtplib
import time
import webbrowser
from datetime import date
from email.message import EmailMessage
from http.cookies import CookieError, SimpleCookie
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlsplit

HTML = '<!DOCTYPE html>\n<html lang="fa" dir="rtl">\n<head>\n  <meta charset="UTF-8" />\n  <meta name="viewport" content="width=device-width, initial-scale=1.0" />\n  <title>IdeaVault | دفتر هوشمند ایده\u200cها</title>\n  <link rel="preconnect" href="https://fonts.googleapis.com">\n  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>\n  <link href="https://fonts.googleapis.com/css2?family=Vazirmatn:wght@400;500;600;700;800&display=swap" rel="stylesheet">\n\n  <style>\n    :root {\n      --bg: #fafafc;\n      --card: #ffffff;\n      --primary: #7c4dff;\n      --primary-dark: #6937ee;\n      --soft-purple: #ede7f6;\n      --purple-50: #f7f3ff;\n      --text: #17224a;\n      --muted: #8991ad;\n      --border: #e9eaf3;\n      --green: #18b979;\n      --green-bg: #e3f8ef;\n      --yellow: #f3a91b;\n      --yellow-bg: #fff3d8;\n      --red: #ed5d68;\n      --shadow: 0 12px 35px rgba(71, 55, 130, .07);\n      --radius-xl: 20px;\n      --radius-lg: 14px;\n      --radius-md: 11px;\n    }\n\n    * { box-sizing: border-box; }\n\n    html, body {\n      margin: 0;\n      min-height: 100%;\n      background:\n        radial-gradient(circle at 80% 0%, rgba(124,77,255,.035), transparent 28%),\n        var(--bg);\n      color: var(--text);\n      font-family: "Vazirmatn", Tahoma, Arial, sans-serif;\n    }\n\n    body {\n      padding-bottom: 35px;\n    }\n\n    button, input, textarea, select {\n      font: inherit;\n    }\n\n    button {\n      border: 0;\n      cursor: pointer;\n    }\n\n    .topbar {\n      height: 64px;\n      background: rgba(255,255,255,.94);\n      border-bottom: 1px solid #eeeeF5;\n      display: flex;\n      align-items: center;\n      justify-content: space-between;\n      padding: 0 54px;\n      position: sticky;\n      top: 0;\n      z-index: 20;\n      backdrop-filter: blur(12px);\n    }\n\n    .brand {\n      display: flex;\n      align-items: center;\n      gap: 11px;\n      font-size: 18px;\n      font-weight: 800;\n      color: var(--primary);\n    }\n\n    .brand small {\n      color: #263154;\n      font-size: 13px;\n      font-weight: 500;\n      padding-left: 18px;\n      border-left: 1px solid var(--border);\n    }\n\n    .brand-icon {\n      width: 30px;\n      height: 30px;\n      color: var(--primary);\n    }\n\n    .top-actions {\n      display: flex;\n      align-items: center;\n      direction: ltr;\n      gap: 14px;\n    }\n\n    .icon-btn {\n      width: 36px;\n      height: 36px;\n      border-radius: 50%;\n      display: grid;\n      place-items: center;\n      background: transparent;\n      color: #28345e;\n      transition: .2s ease;\n    }\n\n    .icon-btn:hover {\n      background: var(--purple-50);\n      color: var(--primary);\n    }\n\n    .avatar {\n      width: 32px;\n      height: 32px;\n      border-radius: 50%;\n      background: linear-gradient(135deg, #8e5cff, #6b3ef4);\n      color: white;\n      display: grid;\n      place-items: center;\n    }\n\n    .container {\n      width: min(1450px, calc(100% - 88px));\n      margin: 30px auto 0;\n    }\n\n    .card {\n      background: var(--card);\n      border: 1px solid rgba(229,228,240,.8);\n      border-radius: var(--radius-xl);\n      box-shadow: var(--shadow);\n    }\n\n    /* New Idea */\n    .idea-card {\n      overflow: hidden;\n    }\n\n    .section-heading {\n      min-height: 65px;\n      display: flex;\n      align-items: center;\n      justify-content: flex-start;\n      gap: 12px;\n      padding: 0 24px;\n      border-bottom: 1px solid #f1f1f6;\n    }\n\n    .heading-icon {\n      width: 42px;\n      height: 42px;\n      border-radius: 12px;\n      background: var(--soft-purple);\n      color: var(--primary);\n      display: grid;\n      place-items: center;\n      flex: 0 0 auto;\n    }\n\n    .section-heading h1,\n    .library-title h2 {\n      margin: 0;\n      font-size: 20px;\n      font-weight: 800;\n      letter-spacing: -.3px;\n    }\n\n    .idea-form {\n      display: grid;\n      grid-template-columns: minmax(0, 1.7fr) minmax(330px, .95fr);\n      direction: ltr;\n      min-height: 320px;\n    }\n\n    .form-right,\n    .form-left {\n      direction: rtl;\n      padding: 22px 24px;\n    }\n\n    .form-right {\n      border-left: 1px solid #ededf5;\n    }\n\n    .field {\n      margin-bottom: 18px;\n    }\n\n    .field:last-child {\n      margin-bottom: 0;\n    }\n\n    .field-label {\n      display: flex;\n      align-items: center;\n      gap: 7px;\n      margin-bottom: 8px;\n      color: #273255;\n      font-size: 13px;\n      font-weight: 700;\n    }\n\n    .field-label svg {\n      color: #5e6685;\n    }\n\n    .control,\n    .textarea {\n      width: 100%;\n      border: 1px solid #dfe2ee;\n      background: #fff;\n      color: var(--text);\n      border-radius: 11px;\n      outline: none;\n      transition: .2s ease;\n    }\n\n    .control {\n      height: 48px;\n      padding: 0 15px;\n    }\n\n    .textarea {\n      min-height: 136px;\n      padding: 13px 15px;\n      resize: vertical;\n      line-height: 1.9;\n    }\n\n    .control::placeholder,\n    .textarea::placeholder {\n      color: #a8aec1;\n    }\n\n    .control:focus,\n    .textarea:focus,\n    .search:focus {\n      border-color: #b9a4ff;\n      box-shadow: 0 0 0 4px rgba(124,77,255,.08);\n    }\n\n    .select-wrap {\n      position: relative;\n    }\n\n    .select-wrap select {\n      appearance: none;\n      padding-left: 42px;\n      cursor: pointer;\n    }\n\n    .select-arrow {\n      position: absolute;\n      left: 14px;\n      top: 50%;\n      transform: translateY(-50%);\n      pointer-events: none;\n      color: #65708d;\n    }\n\n    .chips {\n      min-height: 48px;\n      border: 1px solid #dfe2ee;\n      border-radius: 11px;\n      padding: 7px 9px;\n      display: flex;\n      align-items: center;\n      gap: 7px;\n      flex-wrap: wrap;\n    }\n\n    .chip {\n      display: inline-flex;\n      align-items: center;\n      gap: 5px;\n      padding: 6px 10px;\n      background: #f0eaff;\n      color: #6842e8;\n      border-radius: 999px;\n      font-size: 11px;\n      font-weight: 600;\n    }\n\n    .chip button {\n      background: transparent;\n      color: inherit;\n      padding: 0;\n      line-height: 1;\n    }\n\n    .chip-input {\n      border: 0;\n      outline: 0;\n      flex: 1;\n      min-width: 90px;\n      color: var(--text);\n      background: transparent;\n      direction: rtl;\n    }\n\n    .status-option {\n      display: flex;\n      align-items: center;\n      gap: 8px;\n    }\n\n    .status-dot {\n      width: 9px;\n      height: 9px;\n      border-radius: 50%;\n      background: var(--green);\n      box-shadow: 0 0 0 4px rgba(24,185,121,.08);\n    }\n\n    .save-btn {\n      width: 100%;\n      height: 48px;\n      margin-top: 2px;\n      border-radius: 11px;\n      color: #fff;\n      font-weight: 700;\n      background: linear-gradient(135deg, #7c4dff, #6e3df2);\n      box-shadow: 0 10px 22px rgba(124,77,255,.20);\n      transition: transform .2s ease, box-shadow .2s ease;\n    }\n\n    .save-btn:hover {\n      transform: translateY(-2px);\n      box-shadow: 0 14px 27px rgba(124,77,255,.28);\n    }\n\n    .save-btn:active {\n      transform: translateY(0);\n    }\n\n    /* Library */\n    .library-card {\n      margin-top: 22px;\n      padding: 18px 12px 10px;\n    }\n\n    .library-header {\n      padding: 0 12px 15px;\n      display: flex;\n      align-items: center;\n      justify-content: space-between;\n      gap: 20px;\n    }\n\n    .library-title {\n      display: flex;\n      align-items: center;\n      gap: 12px;\n    }\n\n    .library-icon {\n      color: var(--primary);\n      width: 35px;\n      height: 35px;\n    }\n\n    .count {\n      padding: 5px 10px;\n      background: #f0eaff;\n      color: #6e45ed;\n      border-radius: 999px;\n      font-size: 11px;\n      font-weight: 700;\n    }\n\n    .library-tools {\n      display: flex;\n      gap: 12px;\n      align-items: center;\n    }\n\n    .search-wrap {\n      position: relative;\n    }\n\n    .search {\n      width: 365px;\n      height: 44px;\n      border: 1px solid #e0e2ed;\n      border-radius: 11px;\n      outline: none;\n      padding: 0 42px 0 15px;\n      color: var(--text);\n      transition: .2s ease;\n      background: #fff;\n    }\n\n    .search-icon {\n      position: absolute;\n      right: 14px;\n      top: 50%;\n      transform: translateY(-50%);\n      color: #8991aa;\n    }\n\n    .filter-btn {\n      height: 44px;\n      padding: 0 18px;\n      border-radius: 11px;\n      color: #6741e8;\n      background: #f1ebff;\n      display: flex;\n      align-items: center;\n      gap: 7px;\n      font-weight: 700;\n      transition: .2s ease;\n    }\n\n    .filter-btn:hover {\n      background: #e7ddff;\n    }\n\n    .idea-list {\n      border-top: 1px solid #f0f1f6;\n    }\n\n    .list-header,\n    .idea-row {\n      display: grid;\n      grid-template-columns: 55px minmax(300px, 2.5fr) minmax(110px, 1fr) minmax(120px, 1fr) minmax(90px, .7fr);\n      align-items: center;\n      column-gap: 20px;\n    }\n\n    .list-header {\n      min-height: 42px;\n      padding: 0 15px;\n      color: #6e7692;\n      font-size: 11px;\n      font-weight: 700;\n      background: #fbfbfd;\n    }\n\n    .idea-row {\n      min-height: 76px;\n      margin-top: 9px;\n      padding: 0 15px;\n      border: 1px solid #f0f1f6;\n      border-radius: 13px;\n      background: #fff;\n      transition: .2s ease;\n    }\n\n    .idea-row:hover {\n      transform: translateY(-1px);\n      border-color: #ddd4f9;\n      box-shadow: 0 7px 20px rgba(68,52,130,.06);\n    }\n\n    .number {\n      color: #303b64;\n      font-size: 12px;\n      text-align: center;\n    }\n\n    .idea-main {\n      display: flex;\n      align-items: center;\n      gap: 12px;\n      min-width: 0;\n    }\n\n    .idea-icon {\n      width: 40px;\n      height: 40px;\n      border-radius: 50%;\n      flex: 0 0 auto;\n      display: grid;\n      place-items: center;\n      background: #f0eaff;\n      color: var(--primary);\n    }\n\n    .idea-info {\n      min-width: 0;\n    }\n\n    .idea-name {\n      font-size: 14px;\n      font-weight: 800;\n      color: #20294c;\n      margin-bottom: 4px;\n    }\n\n    .idea-desc {\n      color: #9299af;\n      font-size: 10px;\n      white-space: nowrap;\n      overflow: hidden;\n      text-overflow: ellipsis;\n    }\n\n    .badge {\n      width: max-content;\n      display: inline-flex;\n      align-items: center;\n      gap: 6px;\n      padding: 7px 11px;\n      border-radius: 999px;\n      font-size: 10px;\n      font-weight: 700;\n    }\n\n    .badge-purple {\n      color: #6841e8;\n      background: #f0eaff;\n    }\n\n    .badge-green {\n      color: #0c9b68;\n      background: var(--green-bg);\n    }\n\n    .badge-yellow {\n      color: #e69a0b;\n      background: var(--yellow-bg);\n    }\n\n    .date {\n      color: #6f7791;\n      font-size: 11px;\n      display: flex;\n      align-items: center;\n      gap: 7px;\n    }\n\n    .more {\n      width: 34px;\n      height: 34px;\n      border-radius: 9px;\n      background: transparent;\n      color: #2b3558;\n      font-size: 21px;\n      line-height: 1;\n    }\n\n    .more:hover {\n      background: var(--purple-50);\n    }\n\n    /* Design note */\n    .note {\n      margin-top: 22px;\n      border: 1px solid #d9ceff;\n      background: #faf8ff;\n      border-radius: 16px;\n      padding: 18px 25px;\n      display: flex;\n      align-items: flex-start;\n      gap: 20px;\n      color: #4f5877;\n    }\n\n    .note-icon {\n      width: 48px;\n      height: 48px;\n      flex: 0 0 auto;\n      border-radius: 50%;\n      background: #e9e0ff;\n      color: var(--primary);\n      display: grid;\n      place-items: center;\n    }\n\n    .note-content {\n      border-right: 3px solid var(--primary);\n      padding-right: 16px;\n    }\n\n    .note-title {\n      color: #6841e8;\n      font-size: 13px;\n      font-weight: 800;\n      margin-bottom: 5px;\n    }\n\n    .note p {\n      margin: 0;\n      font-size: 11px;\n      line-height: 2;\n    }\n\n    /* Toast */\n    .toast {\n      position: fixed;\n      left: 24px;\n      bottom: 24px;\n      background: #20294c;\n      color: #fff;\n      padding: 12px 18px;\n      border-radius: 12px;\n      box-shadow: 0 12px 35px rgba(0,0,0,.15);\n      transform: translateY(100px);\n      opacity: 0;\n      pointer-events: none;\n      transition: .3s ease;\n      font-size: 12px;\n      z-index: 50;\n    }\n\n    .toast.show {\n      transform: translateY(0);\n      opacity: 1;\n    }\n\n    @media (max-width: 1100px) {\n      .container { width: min(94%, 1450px); }\n      .topbar { padding: 0 25px; }\n      .idea-form { grid-template-columns: 1fr; }\n      .form-right { border-left: 0; border-bottom: 1px solid #ededf5; }\n      .search { width: 300px; }\n    }\n\n    @media (max-width: 820px) {\n      .library-header {\n        align-items: stretch;\n        flex-direction: column;\n      }\n\n      .library-tools {\n        width: 100%;\n      }\n\n      .search-wrap,\n      .search {\n        width: 100%;\n      }\n\n      .list-header { display: none; }\n\n      .idea-list {\n        padding-top: 8px;\n      }\n\n      .idea-row {\n        grid-template-columns: 42px 1fr auto;\n        gap: 10px;\n        padding: 13px;\n      }\n\n      .idea-row > .category,\n      .idea-row > .status,\n      .idea-row > .date {\n        display: none;\n      }\n\n      .more { grid-column: 3; grid-row: 1; }\n      .number { grid-column: 1; }\n      .idea-main { grid-column: 2; }\n    }\n\n    @media (max-width: 560px) {\n      .topbar {\n        height: 58px;\n        padding: 0 15px;\n      }\n\n      .brand small {\n        display: none;\n      }\n\n      .container {\n        width: calc(100% - 24px);\n        margin-top: 15px;\n      }\n\n      .section-heading {\n        padding: 0 16px;\n      }\n\n      .form-right,\n      .form-left {\n        padding: 18px 16px;\n      }\n\n      .library-card {\n        padding: 14px 8px 8px;\n      }\n\n      .library-header {\n        padding: 0 8px 13px;\n      }\n\n      .library-title h2 {\n        font-size: 17px;\n      }\n\n      .library-tools {\n        flex-direction: column;\n      }\n\n      .filter-btn {\n        width: 100%;\n        justify-content: center;\n      }\n\n      .note {\n        padding: 15px;\n        gap: 12px;\n      }\n\n      .note-icon {\n        width: 40px;\n        height: 40px;\n      }\n\n      .note p {\n        font-size: 10px;\n      }\n    }\n  </style>\n</head>\n\n<body>\n\n  <header class="topbar">\n    <div class="brand">\n      <small>دفتر هوشمند ایده\u200cها</small>\n      <span>IdeaVault</span>\n      <svg class="brand-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8">\n        <path d="M9 18h6M10 21h4M8.4 14.8A7 7 0 1 1 15.7 15c-.8.7-1.3 1.7-1.5 3h-4.4c-.2-1.2-.7-2.3-1.4-3.2Z"/>\n        <path d="M12 5v4M9.8 7.2 12 9l2.2-1.8"/>\n      </svg>\n    </div>\n\n    <div class="top-actions">\n      <button class="icon-btn" aria-label="اعلان\u200cها">\n        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8">\n          <path d="M18 8a6 6 0 0 0-12 0c0 7-3 7-3 9h18c0-2-3-2-3-9M10 21h4"/>\n        </svg>\n      </button>\n      <button class="icon-btn" aria-label="تنظیمات">\n        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8">\n          <circle cx="12" cy="12" r="3"/>\n          <path d="M19.4 15a1.7 1.7 0 0 0 .3 1.9l.1.1-1.6 1.6-.1-.1a1.7 1.7 0 0 0-1.9-.3 1.7 1.7 0 0 0-1 1.6v.2h-2.4v-.2a1.7 1.7 0 0 0-1-1.6 1.7 1.7 0 0 0-1.9.3l-.1.1-1.6-1.6.1-.1A1.7 1.7 0 0 0 8.6 15a1.7 1.7 0 0 0-1.6-1H6.8v-2.4H7a1.7 1.7 0 0 0 1.6-1 1.7 1.7 0 0 0-.3-1.9l-.1-.1 1.6-1.6.1.1a1.7 1.7 0 0 0 1.9.3 1.7 1.7 0 0 0 1-1.6v-.2h2.4v.2a1.7 1.7 0 0 0 1 1.6 1.7 1.7 0 0 0 1.9-.3l.1-.1 1.6 1.6-.1.1a1.7 1.7 0 0 0-.3 1.9 1.7 1.7 0 0 0 1.6 1h.2V14h-.2a1.7 1.7 0 0 0-1.6 1Z"/>\n        </svg>\n      </button>\n      <button class="icon-btn" aria-label="پروفایل">\n        <span class="avatar">\n          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8">\n            <circle cx="12" cy="8" r="3.2"/>\n            <path d="M5.5 19c.9-3.4 3-5 6.5-5s5.6 1.6 6.5 5"/>\n          </svg>\n        </span>\n      </button>\n    </div>\n  </header>\n\n  <main class="container">\n\n    <!-- ثبت ایده جدید -->\n    <section class="card idea-card">\n      <div class="section-heading">\n        <div class="heading-icon">\n          <svg width="23" height="23" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.9">\n            <path d="M9 18h6M10 21h4M8.5 14.7A7 7 0 1 1 15.7 15c-.8.7-1.3 1.8-1.5 3h-4.4c-.2-1.3-.7-2.4-1.3-3.3Z"/>\n            <path d="M12 5v4"/>\n          </svg>\n        </div>\n        <h1>ثبت ایده جدید</h1>\n      </div>\n\n      <form id="ideaForm" class="idea-form">\n\n        <div class="form-right">\n          <div class="field">\n            <label class="field-label">\n              <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8">\n                <path d="m15 5 4 4M4 20l4.2-1 10.1-10.1a2.8 2.8 0 0 0-4-4L4.2 15 4 20Z"/>\n              </svg>\n              عنوان ایده\n            </label>\n            <input id="title" class="control" type="text" placeholder="عنوان ایده خود را وارد کنید..." />\n          </div>\n\n          <div class="field">\n            <label class="field-label">\n              <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8">\n                <path d="M6 4h9l3 3v13H6zM15 4v4h4M9 12h6M9 16h6"/>\n              </svg>\n              توضیحات\n            </label>\n            <textarea id="description" class="textarea" placeholder="مشکل، راه حل، نکات کلیدی و جزئیات ایده را بنویسید..."></textarea>\n          </div>\n        </div>\n\n        <div class="form-left">\n          <div class="field">\n            <label class="field-label">دسته\u200cبندی</label>\n            <div class="select-wrap">\n              <select id="category" class="control">\n                <option value="">انتخاب دسته\u200cبندی...</option>\n                <option>فناوری</option>\n                <option>کسب\u200cوکار</option>\n                <option>آموزش</option>\n                <option>سلامت</option>\n                <option>بازاریابی</option>\n              </select>\n              <span class="select-arrow">⌄</span>\n            </div>\n          </div>\n\n          <div class="field">\n            <label class="field-label">تگ\u200cها</label>\n            <div class="chips" id="chips">\n              <span class="chip">AI <button type="button" onclick="removeChip(this)">×</button></span>\n              <span class="chip">SaaS <button type="button" onclick="removeChip(this)">×</button></span>\n              <span class="chip">Technology <button type="button" onclick="removeChip(this)">×</button></span>\n              <span class="chip">Startup <button type="button" onclick="removeChip(this)">×</button></span>\n              <input id="tagInput" class="chip-input" placeholder="افزودن تگ..." />\n            </div>\n          </div>\n\n          <div class="field">\n            <label class="field-label">وضعیت</label>\n            <div class="select-wrap">\n              <select id="status" class="control">\n                <option value="ایده خام">ایده خام</option>\n                <option value="فعال">فعال</option>\n                <option value="در حال بررسی">در حال بررسی</option>\n                <option value="متوقف">متوقف</option>\n              </select>\n              <span class="select-arrow">⌄</span>\n            </div>\n          </div>\n\n          <button class="save-btn" type="submit">\n            💾 &nbsp; ذخیره ایده\n          </button>\n        </div>\n\n      </form>\n    </section>\n\n    <!-- کتابخانه -->\n    <section class="card library-card">\n      <div class="library-header">\n        <div class="library-title">\n          <svg class="library-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8">\n            <path d="M4 5.5A2.5 2.5 0 0 1 6.5 3H20v17H6.5A2.5 2.5 0 0 0 4 22z"/>\n            <path d="M4 5.5v14A2.5 2.5 0 0 0 6.5 22M8 3v17"/>\n          </svg>\n          <h2>کتابخانه ایده\u200cها</h2>\n          <span id="ideaCount" class="count">۳ ایده</span>\n        </div>\n\n        <div class="library-tools">\n          <div class="search-wrap">\n            <svg class="search-icon" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">\n              <circle cx="11" cy="11" r="7"/>\n              <path d="m20 20-4-4"/>\n            </svg>\n            <input id="search" class="search" type="search" placeholder="جستجو در ایده\u200cها..." />\n          </div>\n\n          <button id="filterBtn" class="filter-btn" type="button">\n            فیلتر\n            <svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">\n              <path d="M4 6h16M7 12h10M10 18h4"/>\n            </svg>\n          </button>\n        </div>\n      </div>\n\n      <div class="idea-list">\n        <div class="list-header">\n          <span></span>\n          <span>عنوان ایده</span>\n          <span>دسته\u200cبندی</span>\n          <span>وضعیت</span>\n          <span>تاریخ ثبت</span>\n        </div>\n\n        <div id="ideaRows">\n\n          <article class="idea-row" data-search="ai marketing app بازاریابی فناوری ایده خام">\n            <div class="number">1</div>\n\n            <div class="idea-main">\n              <div class="idea-icon">💡</div>\n              <div class="idea-info">\n                <div class="idea-name">AI Marketing App</div>\n                <div class="idea-desc">یک پلتفرم هوشمند برای تحلیل و بهینه\u200cسازی کمپین\u200cهای بازاریابی</div>\n              </div>\n            </div>\n\n            <div class="category">\n              <span class="badge badge-purple">SaaS &nbsp; ▦</span>\n            </div>\n\n            <div class="status">\n              <span class="badge badge-yellow"><span class="status-dot" style="background:#f3a91b"></span> ایده خام</span>\n            </div>\n\n            <div class="date">\n              <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7">\n                <rect x="4" y="5" width="16" height="15" rx="2"/>\n                <path d="M8 3v4M16 3v4M4 10h16"/>\n              </svg>\n              امروز\n            </div>\n\n            <button class="more" type="button" aria-label="گزینه\u200cها">⋮</button>\n          </article>\n\n          <article class="idea-row" data-search="سیستم فروش هوشمند فناوری فعال فروش">\n            <div class="number">2</div>\n\n            <div class="idea-main">\n              <div class="idea-icon">▣</div>\n              <div class="idea-info">\n                <div class="idea-name">سیستم فروش هوشمند</div>\n                <div class="idea-desc">راهکار هوشمند برای افزایش فروش و بهبود تجربه مشتری</div>\n              </div>\n            </div>\n\n            <div class="category">\n              <span class="badge badge-purple">فناوری &nbsp; ▤</span>\n            </div>\n\n            <div class="status">\n              <span class="badge badge-green">● &nbsp; فعال</span>\n            </div>\n\n            <div class="date">\n              <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7">\n                <rect x="4" y="5" width="16" height="15" rx="2"/>\n                <path d="M8 3v4M16 3v4M4 10h16"/>\n              </svg>\n              امروز\n            </div>\n\n            <button class="more" type="button" aria-label="گزینه\u200cها">⋮</button>\n          </article>\n\n          <article class="idea-row" data-search="پلتفرم آموزش آنلاین آموزش توسعه">\n            <div class="number">3</div>\n\n            <div class="idea-main">\n              <div class="idea-icon">🎓</div>\n              <div class="idea-info">\n                <div class="idea-name">پلتفرم آموزش آنلاین</div>\n                <div class="idea-desc">آموزش\u200cهای مهارتی و تخصصی به\u200cصورت تعاملی</div>\n              </div>\n            </div>\n\n            <div class="category">\n              <span class="badge badge-purple">آموزش &nbsp; 🎓</span>\n            </div>\n\n            <div class="status">\n              <span class="badge badge-purple">● &nbsp; توسعه</span>\n            </div>\n\n            <div class="date">\n              <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7">\n                <rect x="4" y="5" width="16" height="15" rx="2"/>\n                <path d="M8 3v4M16 3v4M4 10h16"/>\n              </svg>\n              دیروز\n            </div>\n\n            <button class="more" type="button" aria-label="گزینه\u200cها">⋮</button>\n          </article>\n\n        </div>\n      </div>\n    </section>\n\n    <!-- توضیح طراحی -->\n    <aside class="note">\n      <div class="note-icon">\n        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8">\n          <path d="M9 18h6M10 21h4M8.5 14.7A7 7 0 1 1 15.7 15c-.8.7-1.3 1.8-1.5 3h-4.4c-.2-1.3-.7-2.4-1.3-3.3Z"/>\n          <path d="M12 5v4"/>\n        </svg>\n      </div>\n\n      <div class="note-content">\n        <div class="note-title">پرامپت طراحی:</div>\n        <p>\n          بخش\u200cهای مشخص\u200cشده با طراحی جدید و بخش لیست ایده\u200cها با ظاهری مدرن، تمیز و مینیمال طراحی شدند.\n          کارت\u200cها، فیلدها، چیپ\u200cها و دکمه\u200cها با Border ظریف، Shadow نرم و رنگ\u200cبندی بنفش ملایم طراحی شده\u200cاند\n          تا تجربه\u200cای شبیه یک محصول SaaS حرفه\u200cای ایجاد شود.\n        </p>\n      </div>\n    </aside>\n\n  </main>\n\n  <div id="toast" class="toast">ایده با موفقیت ذخیره شد ✨</div>\n\n  <script>\n    const form = document.getElementById("ideaForm");\n    const title = document.getElementById("title");\n    const description = document.getElementById("description");\n    const category = document.getElementById("category");\n    const status = document.getElementById("status");\n    const tagInput = document.getElementById("tagInput");\n    const chips = document.getElementById("chips");\n    const search = document.getElementById("search");\n    const ideaRows = document.getElementById("ideaRows");\n    const ideaCount = document.getElementById("ideaCount");\n    const toast = document.getElementById("toast");\n\n    function removeChip(button) {\n      button.parentElement.remove();\n    }\n\n    tagInput.addEventListener("keydown", function(e) {\n      if (e.key === "Enter" && this.value.trim()) {\n        e.preventDefault();\n\n        const value = this.value.trim();\n\n        const chip = document.createElement("span");\n        chip.className = "chip";\n        chip.innerHTML = `${escapeHtml(value)} <button type="button">×</button>`;\n\n        chip.querySelector("button").addEventListener("click", () => chip.remove());\n\n        chips.insertBefore(chip, tagInput);\n        this.value = "";\n      }\n    });\n\n    search.addEventListener("input", function() {\n      const query = this.value.trim().toLowerCase();\n      const rows = [...ideaRows.querySelectorAll(".idea-row")];\n\n      rows.forEach(row => {\n        const text = row.dataset.search.toLowerCase();\n        row.style.display = text.includes(query) ? "grid" : "none";\n      });\n    });\n\n    document.getElementById("filterBtn").addEventListener("click", () => {\n      showToast("فیلترها آماده استفاده هستند");\n    });\n\n    form.addEventListener("submit", function(e) {\n      e.preventDefault();\n\n      if (!title.value.trim()) {\n        title.focus();\n        showToast("لطفاً عنوان ایده را وارد کنید");\n        return;\n      }\n\n      const selectedCategory = category.value || "فناوری";\n      const selectedStatus = status.value;\n\n      const row = document.createElement("article");\n      row.className = "idea-row";\n      row.dataset.search =\n        `${title.value} ${description.value} ${selectedCategory} ${selectedStatus}`.toLowerCase();\n\n      const statusClass =\n        selectedStatus === "فعال" ? "badge-green" :\n        selectedStatus === "ایده خام" ? "badge-yellow" :\n        "badge-purple";\n\n      row.innerHTML = `\n        <div class="number">جدید</div>\n        <div class="idea-main">\n          <div class="idea-icon">💡</div>\n          <div class="idea-info">\n            <div class="idea-name">${escapeHtml(title.value)}</div>\n            <div class="idea-desc">${escapeHtml(description.value || "بدون توضیحات")}</div>\n          </div>\n        </div>\n        <div class="category">\n          <span class="badge badge-purple">${escapeHtml(selectedCategory)}</span>\n        </div>\n        <div class="status">\n          <span class="badge ${statusClass}">● &nbsp; ${escapeHtml(selectedStatus)}</span>\n        </div>\n        <div class="date">\n          <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7">\n            <rect x="4" y="5" width="16" height="15" rx="2"/>\n            <path d="M8 3v4M16 3v4M4 10h16"/>\n          </svg>\n          امروز\n        </div>\n        <button class="more" type="button">⋮</button>\n      `;\n\n      ideaRows.prepend(row);\n\n      const count = ideaRows.querySelectorAll(".idea-row").length;\n      ideaCount.textContent = `${toPersianNumber(count)} ایده`;\n\n      form.reset();\n      showToast("ایده با موفقیت ذخیره شد ✨");\n    });\n\n    function showToast(message) {\n      toast.textContent = message;\n      toast.classList.add("show");\n      clearTimeout(window.toastTimer);\n      window.toastTimer = setTimeout(() => {\n        toast.classList.remove("show");\n      }, 2300);\n    }\n\n    function toPersianNumber(number) {\n      return String(number).replace(/[0-9]/g, d => "۰۱۲۳۴۵۶۷۸۹"[d]);\n    }\n\n    function escapeHtml(value) {\n      return String(value)\n        .replaceAll("&", "&amp;")\n        .replaceAll("<", "&lt;")\n        .replaceAll(">", "&gt;")\n        .replaceAll(\'"\', "&quot;")\n        .replaceAll("\'", "&#039;");\n    }\n  </script>\n\n</body>\n</html>\n'

AUTH_SCRIPT = r'''<style>
    .top-actions .icon-btn[aria-label="تنظیمات"] { width: 42px; height: 42px; border-radius: 14px; color: #7043e8; background: linear-gradient(145deg, #f8f5ff, #eee8ff); box-shadow: 0 3px 10px rgba(91,60,160,.1), inset 0 0 0 1px rgba(112,67,232,.12); transition: transform .2s ease, box-shadow .2s ease, background .2s ease; }
    .top-actions .icon-btn[aria-label="تنظیمات"] svg { width: 22px; height: 22px; stroke-width: 1.9; filter: drop-shadow(0 1px 1px rgba(45,26,100,.12)); transition: transform .35s ease; }
    .top-actions .icon-btn[aria-label="تنظیمات"] svg circle { fill: rgba(112,67,232,.12); stroke-width: 1.6; }
    .top-actions .icon-btn[aria-label="تنظیمات"]:hover { color: #5f31d4; background: linear-gradient(145deg, #f1ebff, #e7ddff); box-shadow: 0 5px 13px rgba(91,60,160,.16), inset 0 0 0 1px rgba(112,67,232,.18); transform: translateY(-1px); }
    .top-actions .icon-btn[aria-label="تنظیمات"]:hover svg { transform: rotate(35deg); }
    .brand-icon { order: -1; }
    .top-title { display: inline-flex; align-items: center; padding: 7px 12px; border-radius: 12px; color: #6e3df2; background: #f4efff; font-size: 17px; font-weight: 800; }
    .topbar { direction: rtl; }
    .topbar .brand { order: -1; margin-left: auto; }
    .top-actions { position: absolute; left: 54px; }
    .logout-form { display: flex; margin: 0; }
    .logout-button { display: inline-flex; align-items: center; justify-content: center; gap: 8px; min-width: 86px; height: 40px; padding: 0 14px; border: 1px solid rgba(255,255,255,.22); border-radius: 12px; color: #fff; background: linear-gradient(135deg, #e45d69, #c93650); box-shadow: 0 4px 11px rgba(197,54,80,.2), inset 0 1px 0 rgba(255,255,255,.18); direction: rtl; font-size: 13px; font-weight: 700; white-space: nowrap; transition: transform .2s ease, background .2s ease, box-shadow .2s ease; }
    .logout-button:hover { transform: translateY(-1px); background: linear-gradient(135deg, #ed6873, #d34159); box-shadow: 0 6px 15px rgba(197,54,80,.28), inset 0 1px 0 rgba(255,255,255,.2); }
    .logout-button:active { transform: translateY(0); box-shadow: 0 2px 6px rgba(197,54,80,.2); }
    .logout-button:focus-visible { outline: 2px solid #c93650; outline-offset: 3px; }
    .container { width: min(1450px, calc(100% - 108px)); margin-top: 24px; }
    @media (max-width: 1100px) { .container { width: min(94%, 1450px); } }
    @media (max-width: 1100px) { .top-actions { left: 25px; } }
        .theme-toggle { display: grid; place-items: center; width: 52px; height: 40px; padding: 0; border: 1px solid var(--border); border-radius: 999px; color: #7043e8; background: linear-gradient(145deg, #f8f5ff, #eee8ff); box-shadow: 0 3px 10px rgba(91,60,160,.1), inset 0 0 0 1px rgba(112,67,232,.12); transition: transform .2s ease, box-shadow .2s ease, background .2s ease; }
        .theme-toggle svg { width: 21px; height: 21px; }
        .theme-toggle:hover { transform: translateY(-1px); box-shadow: 0 5px 13px rgba(91,60,160,.16), inset 0 0 0 1px rgba(112,67,232,.18); }
        .theme-toggle:focus-visible { outline: 2px solid #7043e8; outline-offset: 2px; }
        html[data-theme="dark"] { color-scheme: dark; --bg: #141821; --card: #1d2330; --text: #edf0f6; --muted: #a1a9ba; --border: #353d4d; --shadow: 0 12px 35px rgba(0,0,0,.24); --green-bg: #17382d; --yellow-bg: #40331b; }
        html[data-theme="dark"] body { background: radial-gradient(circle at 80% 0%, rgba(124,77,255,.08), transparent 28%), var(--bg); color: var(--text); }
        html[data-theme="dark"] .topbar { background: rgba(25,30,41,.96); border-color: #303746; }
        html[data-theme="dark"] .card { border-color: #303746; }
        html[data-theme="dark"] .field-label { color: #d3d9e5; }
        html[data-theme="dark"] .field-label svg, html[data-theme="dark"] .select-arrow { color: #a8b2c5; }
        html[data-theme="dark"] .control, html[data-theme="dark"] .textarea, html[data-theme="dark"] .search, html[data-theme="dark"] .chips { color: var(--text); background: #171c26; border-color: #343d4c; }
        html[data-theme="dark"] .idea-row { color: var(--text); background: #1a202b; border-color: #2a3240; }
        html[data-theme="dark"] .idea-row:hover { border-color: #554779; }
        html[data-theme="dark"] .filter-btn { color: #d0c2ff; background: #302840; }
        html[data-theme="dark"] .filter-btn:hover { background: #3b3150; }
        html[data-theme="dark"] .top-actions .icon-btn { color: #d4d9e3; background: #242b38; }
        html[data-theme="dark"] .top-actions .icon-btn[aria-label="تنظیمات"] { color: #d0c2ff; background: #302840; box-shadow: inset 0 0 0 1px rgba(173,145,255,.18); }
        html[data-theme="dark"] .top-actions .theme-toggle { color: #e2d8ff; background: #39304c; border-color: #514466; }
        html[data-theme="dark"] .logout-button { color: #fff; background: linear-gradient(135deg, #d84d61, #ad304a); border-color: rgba(255,255,255,.12); box-shadow: 0 4px 12px rgba(0,0,0,.25), inset 0 1px 0 rgba(255,255,255,.14); }
        html[data-theme="dark"] .logout-button:hover { background: linear-gradient(135deg, #e45d6e, #bd3b54); box-shadow: 0 6px 16px rgba(0,0,0,.32), inset 0 1px 0 rgba(255,255,255,.18); }
        @media (max-width: 560px) { .top-actions { left: 15px; gap: 6px; } .container { width: calc(100% - 24px); margin-top: 15px; } }
        @media (max-width: 380px) { .top-actions .icon-btn[aria-label="اعلان‌ها"], .top-actions .icon-btn[aria-label="پروفایل"] { display: none; } }
        :root {
            --bg: #f3f7f4;
            --card: #ffffff;
            --primary: #176f5d;
            --primary-dark: #105a4b;
            --soft-purple: #e4f2ec;
            --purple-50: #eff7f3;
            --text: #1d302c;
            --muted: #71817c;
            --border: #dce7e1;
            --green: #19845e;
            --green-bg: #e4f4eb;
            --yellow: #b97517;
            --yellow-bg: #fff2d9;
            --red: #d75b55;
            --shadow: 0 10px 28px rgba(28, 62, 49, .07);
            --radius-xl: 16px;
            --radius-lg: 12px;
            --radius-md: 9px;
        }
        html, body { color: var(--text); background: radial-gradient(ellipse at 7% 12%, rgba(222,111,79,.07), transparent 27%), radial-gradient(ellipse at 88% 0%, rgba(35,130,101,.08), transparent 32%), var(--bg); }
        .topbar { border-color: var(--border); background: rgba(255,255,255,.92); box-shadow: 0 4px 18px rgba(28,62,49,.035); }
        .brand, .brand-icon { color: var(--primary); }
        .brand small { color: #50635d; border-color: var(--border); }
        .container { width: min(1240px, calc(100% - 72px)); margin: 28px auto 0; }
        .card { border-color: var(--border); box-shadow: var(--shadow); }
        .section-heading { min-height: 72px; border-color: #e8efeb; }
        .section-heading h1, .library-title h2 { letter-spacing: 0; }
        .heading-icon, .note-icon { color: var(--primary); background: var(--soft-purple); }
        .control, .textarea, .search, .chips { border-color: #d9e4de; border-radius: 10px; }
        .control:focus, .textarea:focus, .search:focus { border-color: var(--primary); box-shadow: 0 0 0 3px rgba(23,111,93,.12); }
        .filter-btn { color: var(--primary); background: #e7f3ed; }
        .filter-btn:hover { background: #d9ebe2; }
        .save-btn { background: linear-gradient(135deg, #21866b, #176f5d); box-shadow: 0 8px 18px rgba(23,111,93,.18); }
        .save-btn:hover { box-shadow: 0 11px 23px rgba(23,111,93,.24); }
        .chip, .count { color: #286a59; background: #e8f3ed; }
        .idea-icon { color: var(--primary); background: #e7f3ed; }
        .list-header { color: #667a71; background: #f5f8f6; }
        .idea-name { color: var(--text); }
        .note-title { color: var(--primary); }
        .badge-purple { color: #286a59; background: #e8f3ed; }
        .idea-row { border-color: #e7eeea; background: rgba(255,255,255,.82); transition: transform .18s ease, border-color .18s ease, box-shadow .18s ease; }
        .idea-row:hover { border-color: #b9d7c9; box-shadow: 0 7px 18px rgba(28,62,49,.08); }
        .note { border-color: #dce9e2; background: rgba(255,255,255,.72); }
        .top-actions { gap: 9px; }
        .top-actions .theme-toggle { color: var(--primary); background: #e7f3ed; border-color: #d4e6dc; box-shadow: none; }
        .top-actions .theme-toggle:hover { background: #d9ebe2; box-shadow: 0 4px 12px rgba(28,62,49,.1); }
        .logout-button { background: linear-gradient(135deg, #df765b, #c95448); box-shadow: 0 4px 11px rgba(201,84,72,.16); }
        .logout-button:hover { background: linear-gradient(135deg, #e58568, #d36052); box-shadow: 0 6px 14px rgba(201,84,72,.22); }
        .idea-card { animation: dashboard-enter .45s ease both; }
        .library-card { animation: dashboard-enter .45s .08s ease both; }
        .note { animation: dashboard-enter .45s .15s ease both; }
        @keyframes dashboard-enter { from { opacity: 0; transform: translateY(8px); } to { opacity: 1; transform: translateY(0); } }
        html[data-theme="dark"] {
            --bg: #151d1b;
            --card: #202a27;
            --primary: #82c9ae;
            --primary-dark: #67b899;
            --soft-purple: #29443a;
            --purple-50: #293b34;
            --text: #edf4f0;
            --muted: #a7b7af;
            --border: #35443e;
            --green-bg: #244438;
            --yellow-bg: #47391f;
            --shadow: 0 12px 32px rgba(0,0,0,.22);
        }
        html[data-theme="dark"] body { background: radial-gradient(ellipse at 7% 12%, rgba(222,111,79,.07), transparent 27%), radial-gradient(ellipse at 88% 0%, rgba(35,130,101,.1), transparent 32%), var(--bg); }
        html[data-theme="dark"] .topbar { background: rgba(25,35,31,.95); border-color: var(--border); }
        html[data-theme="dark"] .card, html[data-theme="dark"] .idea-row, html[data-theme="dark"] .note { background-color: var(--card); border-color: var(--border); }
        html[data-theme="dark"] .brand small, html[data-theme="dark"] .field-label { color: #d4e1da; }
        html[data-theme="dark"] .section-heading { border-color: var(--border); }
        html[data-theme="dark"] .badge-purple { color: #b7e3d0; background: #29443a; }
        html[data-theme="dark"] .chip, html[data-theme="dark"] .count, html[data-theme="dark"] .idea-icon { color: #b7e3d0; background: #29443a; }
        html[data-theme="dark"] .list-header { color: #b6c7be; background: #202a27; }
        html[data-theme="dark"] .save-btn { background: linear-gradient(135deg, #238b70, #176f5d); }
        html[data-theme="dark"] .idea-desc, html[data-theme="dark"] .date, html[data-theme="dark"] .number, html[data-theme="dark"] .more, html[data-theme="dark"] .note { color: #b6c7be; }
        html[data-theme="dark"] .more:hover { background: #293b34; }
        html[data-theme="dark"] .filter-btn, html[data-theme="dark"] .top-actions .theme-toggle { color: #b7e3d0; background: #29443a; border-color: #40594e; }
        html[data-theme="dark"] .idea-row:hover { border-color: #587666; }
        @media (max-width: 1100px) {
            .container { width: min(94%, 980px); }
            .topbar { padding-inline: 22px; }
        }
        @media (max-width: 820px) {
            .container { width: calc(100% - 40px); margin-top: 22px; }
            .topbar { padding-inline: 20px; }
            .idea-row { grid-template-columns: 34px minmax(190px, 1fr) minmax(82px, auto) minmax(90px, auto) 32px; column-gap: 10px; }
            .idea-row > .category, .idea-row > .status, .idea-row > .date { display: flex; align-items: center; }
            .number, .idea-main, .more { grid-column: auto; grid-row: auto; }
        }
        @media (max-width: 560px) {
            .topbar { height: 60px; padding-inline: 12px; }
            .topbar .brand { gap: 7px; font-size: 16px; }
            .brand-icon { width: 26px; height: 26px; }
            .top-actions { left: 12px; gap: 6px; }
            .top-actions .theme-toggle { width: 40px; height: 38px; }
            .logout-button { min-width: 64px; height: 38px; padding-inline: 9px; font-size: 12px; }
            .container { width: calc(100% - 24px); margin-top: 16px; }
            .section-heading { min-height: 62px; padding-inline: 16px; }
            .section-heading h1, .library-title h2 { font-size: 17px; }
            .idea-row { grid-template-columns: 28px minmax(0, 1fr) 32px; grid-template-areas: "number idea more" "status status status"; grid-template-rows: auto auto; gap: 9px 8px; padding: 13px 11px; }
            .idea-row > .category, .idea-row > .date { display: none; }
            .idea-row > .status { grid-area: status; justify-content: flex-start; padding-inline-start: 36px; }
            .idea-row > .number { grid-area: number; align-self: center; }
            .idea-row > .idea-main { grid-area: idea; }
            .idea-row > .more { grid-area: more; }
            .idea-info { overflow-wrap: anywhere; }
            .idea-name { font-size: 13px; }
            .idea-desc { font-size: 11px; line-height: 1.7; white-space: normal; display: -webkit-box; -webkit-box-orient: vertical; -webkit-line-clamp: 2; overflow: hidden; }
            .library-tools { flex-direction: row; gap: 8px; }
            .search-wrap, .search { width: 100%; min-width: 0; }
            .filter-btn { width: auto; flex: 0 0 auto; justify-content: center; padding-inline: 13px; }
            .note { padding: 14px; }
        }
        @media (max-width: 380px) {
            .container { width: calc(100% - 20px); }
            .topbar .brand { font-size: 15px; }
            .top-actions { left: 10px; }
            .logout-button { min-width: 58px; }
            .library-card { padding-inline: 8px; }
            .library-header { padding-inline: 6px; }
        }
        @media (prefers-reduced-motion: reduce) {
            *, *::before, *::after { animation-duration: .01ms !important; animation-iteration-count: 1 !important; scroll-behavior: auto !important; transition-duration: .01ms !important; }
        }
</style>
<script>
    (() => {
        const actions = document.querySelector(".top-actions");
        if (!actions) return;

        actions.querySelectorAll(".icon-btn").forEach(button => button.remove());

        const toggle = document.createElement("button");
        toggle.type = "button";
        toggle.className = "theme-toggle";
        const sunIcon = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" aria-hidden="true"><circle cx="12" cy="12" r="4"/><path d="M12 2v2m0 16v2M4.93 4.93l1.42 1.42m11.3 11.3 1.42 1.42M2 12h2m16 0h2M4.93 19.07l1.42-1.42m11.3-11.3 1.42-1.42"/></svg>';
        const moonIcon = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" aria-hidden="true"><path d="M20.9 13A8.5 8.5 0 0 1 11 3.1 8.5 8.5 0 1 0 20.9 13Z"/></svg>';
        actions.append(toggle);

        const logoutForm = document.createElement("form");
        logoutForm.className = "logout-form";
        logoutForm.method = "post";
        logoutForm.action = "/logout";
        logoutForm.innerHTML = '<button class="logout-button" type="submit" aria-label="خروج از حساب">خروج</button>';
        actions.append(logoutForm);

        function applyTheme(theme) {
            document.documentElement.dataset.theme = theme;
            toggle.innerHTML = theme === "dark" ? moonIcon : sunIcon;
            const nextTheme = theme === "dark" ? "روشن" : "تیره";
            toggle.setAttribute("aria-label", `تغییر تم به ${nextTheme}`);
            toggle.title = `تغییر تم به ${nextTheme}`;
            try { localStorage.setItem("ideon-theme", theme); } catch {}
        }

        let initialTheme = "light";
        try {
            const savedTheme = localStorage.getItem("ideon-theme");
            if (savedTheme === "dark" || savedTheme === "light") initialTheme = savedTheme;
        } catch {}
        toggle.addEventListener("click", () => applyTheme(document.documentElement.dataset.theme === "dark" ? "light" : "dark"));
        applyTheme(initialTheme);
    })();
</script>
</body>'''


def gregorian_to_jalali(gregorian_date):
    gy, gm, gd = gregorian_date.year, gregorian_date.month, gregorian_date.day
    month_days = [31, 31, 31, 31, 31, 31, 30, 30, 30, 30, 30, 29]

    gy -= 1600
    gm -= 1
    gd -= 1
    day_number = 365 * gy + (gy + 3) // 4 - (gy + 99) // 100 + (gy + 399) // 400
    day_number += sum([31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31][:gm])
    if gm > 1 and (gy % 4 == 0 and (gy % 100 != 0 or gy % 400 == 0)):
        day_number += 1
    day_number += gd

    jalali_day = day_number - 79
    cycle = jalali_day // 12053
    jalali_day %= 12053
    jy = 979 + 33 * cycle + 4 * (jalali_day // 1461)
    jalali_day %= 1461
    if jalali_day >= 366:
        jy += (jalali_day - 1) // 365
        jalali_day = (jalali_day - 1) % 365

    for month, days in enumerate(month_days):
        if jalali_day < days:
            jm = month + 1
            jd = jalali_day + 1
            break
        jalali_day -= days
    return jy, jm, jd


PASSWORD_HASH_ROUNDS = 310_000
EMAIL_RECOVERY_CODE_TTL = 600


def normalize_email(value):
    if not isinstance(value, str):
        return ""
    return value.strip().lower()


def normalize_username(value):
    if not isinstance(value, str):
        return ""
    return value.strip().lower()


def send_recovery_email(email, code):
    host = os.environ.get("IDEAVAULT_SMTP_HOST")
    if not host:
        print(f"[IdeaVault] Recovery code for {email}: {code}")
        return False

    port = int(os.environ.get("IDEAVAULT_SMTP_PORT", "587"))
    username = os.environ.get("IDEAVAULT_SMTP_USER")
    password = os.environ.get("IDEAVAULT_SMTP_PASS")
    sender = os.environ.get("IDEAVAULT_SMTP_FROM", "noreply@ideavault.local")

    message = EmailMessage()
    message["Subject"] = "کد بازیابی رمز عبور IdeaVault"
    message["From"] = sender
    message["To"] = email
    message.set_content(
        f"کد بازیابی شما: {code}\n\nاین کد فقط برای 10 دقیقه معتبر است.\n\nاگر شما این درخواست را انجام نداده‌اید، این ایمیل را نادیده بگیرید."
    )

    try:
        if port == 465:
            server = smtplib.SMTP_SSL(host, port)
        else:
            server = smtplib.SMTP(host, port)
            if not port == 25:
                server.starttls()
        if username and password:
            server.login(username, password)
        server.send_message(message)
        server.quit()
        return True
    except Exception as error:
        print(f"[IdeaVault] SMTP send failed: {error}")
        return False


def get_credentials_path():
    app_data = Path(os.environ.get("APPDATA", str(Path.home())))
    return app_data / "IdeaVault" / "credentials.json"


def load_credentials(path):
    if not path.exists():
        return None
    try:
        credentials = json.loads(path.read_text(encoding="utf-8"))
        salt = base64.b64decode(credentials["salt"], validate=True)
        password_hash = base64.b64decode(credentials["password_hash"], validate=True)
        username = normalize_username(credentials.get("username", ""))
        email = normalize_email(credentials.get("email", ""))
    except (OSError, ValueError, KeyError, TypeError, json.JSONDecodeError) as error:
        raise SystemExit("فایل اطلاعات ورود قابل خواندن نیست؛ آن را بررسی کنید.") from error
    if not isinstance(username, str) or len(salt) != 16 or len(password_hash) != 32:
        raise SystemExit("فایل اطلاعات ورود معتبر نیست؛ آن را بررسی کنید.")
    return {"username": username, "email": email, "salt": salt, "password_hash": password_hash}


def create_credentials(path, username, password, email=""):
    normalized_username = normalize_username(username)
    salt = secrets.token_bytes(16)
    password_hash = hashlib.pbkdf2_hmac(
        "sha256", password.encode("utf-8"), salt, PASSWORD_HASH_ROUNDS
    )
    credentials = {
        "username": normalized_username,
        "email": normalize_email(email),
        "salt": base64.b64encode(salt).decode("ascii"),
        "password_hash": base64.b64encode(password_hash).decode("ascii"),
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(credentials), encoding="utf-8")
    return {"username": normalized_username, "email": normalize_email(email), "salt": salt, "password_hash": password_hash}


LOGIN_HTML = '''<!DOCTYPE html>
<html lang="fa" dir="rtl">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>{{TITLE}}</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Vazirmatn:wght@400;500;600;700;800&display=swap" rel="stylesheet">
  <style>
    * { box-sizing: border-box; }
    :root { color-scheme: dark; font-family: "Vazirmatn", Tahoma, sans-serif; }
    body { display: grid; min-height: 100vh; margin: 0; padding: 24px; place-items: center; color: #f8f3ff; background: radial-gradient(ellipse at 78% 100%, rgba(133,31,110,.42), transparent 42%), radial-gradient(ellipse at 8% 12%, rgba(81,42,112,.2), transparent 36%), #160d25; font-family: inherit; }
    .login { width: min(100%, 630px); padding: 34px 56px 36px; border: 1px solid rgba(211,174,229,.16); border-radius: 44px; background: rgba(20,12,34,.32); box-shadow: 0 28px 90px rgba(8,3,18,.22), inset 0 1px 0 rgba(255,255,255,.025); }
    .brand { display: flex; flex-direction: column; align-items: center; gap: 14px; margin-bottom: 18px; color: #c49bff; font-size: 12px; font-weight: 800; letter-spacing: 3px; }
    .brand-mark { display: grid; width: 56px; height: 56px; place-items: center; border-radius: 20px; color: #fff; background: linear-gradient(145deg, #d54eea, #7252f5); box-shadow: 0 10px 25px rgba(150,63,226,.3); }
    .brand-mark svg { width: 27px; height: 27px; fill: currentColor; stroke: none; }
    .brand > span:nth-child(2) { display: none; }
    h1 { margin: 0 0 5px; text-align: center; font-size: 36px; line-height: 1.45; font-weight: 700; }
    .hint { margin: 0 0 28px; color: #b3a4c2; text-align: center; font-size: 13px; }
    label { display: block; margin: 17px 0 7px; color: #e6dceb; font-size: 14px; font-weight: 700; }
    input { width: 100%; height: 54px; padding: 0 16px; border: 1px solid rgba(205,174,221,.17); border-radius: 17px; color: #fbf7ff; background: rgba(14,8,26,.52); font: inherit; transition: border-color .2s ease, box-shadow .2s ease, background .2s ease; }
    input::placeholder { color: #81738f; }
    input:focus { border-color: #b44ce1; outline: 0; background: rgba(19,10,32,.8); box-shadow: 0 0 0 3px rgba(184,70,225,.15); }
    .password-field { position: relative; }
    .password-field input { padding-right: 54px; }
    .password-toggle {
      position: absolute;
      top: 50%;
      right: 10px;
      display: grid;
      width: 36px;
      height: 36px;
      margin: 0;
      padding: 0;
      place-items: center;
      transform: translateY(-50%);
      border: 1px solid rgba(206,174,233,.22);
      border-radius: 12px;
      color: #d8c5f4;
      background: linear-gradient(180deg, rgba(124,77,255,.14), rgba(255,255,255,.03));
      box-shadow: inset 0 1px 0 rgba(255,255,255,.15), 0 4px 12px rgba(102,73,164,.12);
      transition: transform .18s ease, border-color .18s ease, box-shadow .18s ease, color .18s ease, background .18s ease;
    }
    .password-toggle:hover {
      color: #f5e7ff;
      border-color: rgba(214,180,255,.5);
      background: linear-gradient(180deg, rgba(152,110,255,.18), rgba(255,255,255,.05));
      box-shadow: inset 0 1px 0 rgba(255,255,255,.2), 0 6px 18px rgba(132,99,220,.16);
      transform: translateY(-50%) scale(1.04);
    }
    .password-toggle:active { transform: translateY(-50%) scale(.98); }
    .password-toggle:focus-visible {
      outline: 2px solid rgba(210,156,255,.9);
      outline-offset: 2px;
      box-shadow: 0 0 0 4px rgba(182,134,255,.18), inset 0 1px 0 rgba(255,255,255,.2);
    }
    .password-toggle svg { width: 18px; height: 18px; }
    .error { margin: 14px 0 0; color: #ff8998; font-size: 13px; }
    .auth-switch {
      display: flex;
      align-items: center;
      justify-content: center;
      margin-top: 16px;
    }
    .inline-link {
      display: inline-flex;
      align-items: center;
      justify-content: center;
      min-height: 42px;
      padding: 7px 16px;
      border: 1px solid rgba(211,174,229,.2);
      border-radius: 13px;
      color: #d9c1ec;
      background: linear-gradient(135deg, rgba(129,83,169,.13), rgba(255,255,255,.025));
      box-shadow: inset 0 1px 0 rgba(255,255,255,.045);
      font: inherit;
      font-size: 13px;
      font-weight: 600;
      line-height: 1.7;
      text-align: center;
      text-decoration: none;
      transition: color .2s ease, border-color .2s ease, background .2s ease, box-shadow .2s ease, transform .2s ease;
    }
    .inline-link:hover {
      transform: translateY(-1px);
      color: #fff0ff;
      border-color: rgba(218,163,244,.42);
      background: linear-gradient(135deg, rgba(153,83,190,.23), rgba(255,255,255,.045));
      box-shadow: 0 6px 18px rgba(9,3,18,.16), inset 0 1px 0 rgba(255,255,255,.08);
    }
    .forgot-password { display: flex; align-items: center; justify-content: center; width: fit-content; max-width: 100%; min-height: 42px; margin: 16px auto 0; padding: 7px 15px; border: 1px solid rgba(211,174,229,.2); border-radius: 13px; color: #d9c1ec; background: linear-gradient(135deg, rgba(129,83,169,.13), rgba(255,255,255,.025)); box-shadow: inset 0 1px 0 rgba(255,255,255,.045); font: inherit; font-size: 13px; font-weight: 600; line-height: 1.7; text-align: center; cursor: pointer; transition: color .2s ease, border-color .2s ease, background .2s ease, box-shadow .2s ease, transform .2s ease; }
    .forgot-password:hover { transform: translateY(-1px); color: #fff0ff; border-color: rgba(218,163,244,.42); background: linear-gradient(135deg, rgba(153,83,190,.23), rgba(255,255,255,.045)); box-shadow: 0 6px 18px rgba(9,3,18,.16), inset 0 1px 0 rgba(255,255,255,.08); }
    .forgot-password:active { transform: translateY(0); }
    .forgot-password:focus-visible, .recovery-close:focus-visible { outline: 2px solid #c55aec; outline-offset: 3px; }
    .recovery-dialog { width: min(100% - 32px, 500px); padding: 28px; border: 1px solid rgba(211,174,229,.2); border-radius: 24px; color: #f8f3ff; background: #20142d; box-shadow: 0 28px 90px rgba(8,3,18,.5); font: inherit; }
    .recovery-dialog::backdrop { background: rgba(8,3,18,.72); backdrop-filter: blur(4px); }
    .recovery-dialog h2 { margin: 0 0 12px; font-size: 20px; }
    .recovery-dialog p { margin: 0 0 14px; color: #c5b5d1; font-size: 14px; line-height: 1.9; }
    .recovery-close { min-height: 42px; padding: 0 18px; border-radius: 12px; color: #fff; background: #7548d6; font: inherit; font-weight: 700; cursor: pointer; }
    button[type="submit"] { width: 100%; min-height: 56px; margin-top: 22px; border: 0; border-radius: 17px; color: #fff; background: linear-gradient(105deg, #8751f2 0%, #cb35df 100%); box-shadow: 0 9px 24px rgba(153,56,213,.17); font: inherit; font-weight: 700; cursor: pointer; transition: filter .2s ease, transform .2s ease, box-shadow .2s ease; }
    button[type="submit"]:hover { transform: translateY(-1px); filter: brightness(1.08); box-shadow: 0 12px 28px rgba(153,56,213,.25); }
    button[type="submit"]:focus-visible { outline: 2px solid #f1c5ff; outline-offset: 3px; }
    @media (max-width: 520px) { body { padding: 16px; } .login { padding: 30px 22px; border-radius: 30px; } .brand { margin-bottom: 15px; } h1 { font-size: 28px; } .hint { margin-bottom: 23px; } }
  </style>
</head>
<body>
  <main class="login">
    <div class="brand"><span class="brand-mark" aria-hidden="true"><svg viewBox="0 0 24 24"><path d="m12 1.8 2.35 7.85L22.2 12l-7.85 2.35L12 22.2l-2.35 7.85L1.8 12l7.85-2.35L12 1.8Z"/></svg></span><span>IDEAVAULT</span><span>{{EYEBROW}}</span></div>
        <h1>{{HEADING}}</h1>
        <p class="hint">{{HINT}}</p>
        <form method="post" action="{{ACTION}}" autocomplete="on">
      <label for="username">نام کاربری</label>
            <input id="username" name="username" type="text" maxlength="80" autocomplete="username" required autofocus />
      {{EMAIL_FIELD}}
      <label for="password">رمز عبور</label>
            <div class="password-field">
                <input id="password" name="password" type="password" maxlength="1024" autocomplete="{{PASSWORD_AUTOCOMPLETE}}" required />
                <button class="password-toggle" type="button" aria-label="نمایش رمز عبور" aria-pressed="false" aria-controls="password"></button>
            </div>
            {{CONFIRMATION}}
      {{ERROR}}
            <button type="submit">{{BUTTON}}</button>
    </form>
        {{SIGNUP_LINK}}
        {{RESET_ACCOUNT_LINK}}
        {{FORGOT_PASSWORD}}
  </main>
    <script>
        const eyeIcon = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" aria-hidden="true"><path d="M2 12s3.6-7 10-7 10 7 10 7-3.6 7-10 7-10-7-10-7Z"/><circle cx="12" cy="12" r="3"/></svg>';
        const eyeOffIcon = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" aria-hidden="true"><path d="m3 3 18 18M10.6 10.6a2 2 0 0 0 2.8 2.8"/><path d="M9.9 5.2A11 11 0 0 1 12 5c6.4 0 10 7 10 7a15 15 0 0 1-3.1 3.7M6.2 6.2C3.5 8 2 12 2 12s3.6 7 10 7c1.1 0 2.1-.2 3-.5"/></svg>';
        document.querySelectorAll(".password-toggle").forEach(toggle => {
            const input = document.getElementById(toggle.getAttribute("aria-controls"));
            if (!input) return;
            toggle.innerHTML = eyeIcon;
            toggle.addEventListener("click", () => {
                const isVisible = input.type === "password";
                input.type = isVisible ? "text" : "password";
                toggle.innerHTML = isVisible ? eyeOffIcon : eyeIcon;
                toggle.setAttribute("aria-pressed", String(isVisible));
                toggle.setAttribute("aria-label", isVisible ? "پنهان کردن رمز عبور" : "نمایش رمز عبور");
            });
        });
        const recoveryDialog = document.getElementById("recovery-dialog");
        document.getElementById("forgot-password")?.addEventListener("click", () => recoveryDialog.showModal());
        document.getElementById("recovery-close")?.addEventListener("click", () => recoveryDialog.close());
    </script>
</body>
</html>'''


class IdeaVaultHandler(BaseHTTPRequestHandler):
    page_html = ""
    credentials = None
    credentials_path = None
    active_sessions = set()
    pending_recovery = None

    def _send_html(self, content, status=200, headers=()):
        body = content.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        for name, value in headers:
            self.send_header(name, value)
        self.end_headers()
        self.wfile.write(body)

    def _redirect(self, location, cookie=None):
        self.send_response(303)
        self.send_header("Location", location)
        self.send_header("Content-Length", "0")
        self.send_header("Cache-Control", "no-store")
        if cookie:
            self.send_header("Set-Cookie", cookie)
        self.end_headers()

    def _reset_account(self):
        self.credentials = None
        type(self).credentials = None
        type(self).pending_recovery = None
        if self.credentials_path is not None:
            try:
                self.credentials_path.unlink()
            except FileNotFoundError:
                pass
            except OSError:
                pass
        self.active_sessions.clear()

    def _has_session(self):
        session = self._session_id()
        return session is not None and session in self.active_sessions

    def _session_id(self):
        cookie = SimpleCookie()
        try:
            cookie.load(self.headers.get("Cookie", ""))
        except CookieError:
            return None
        session = cookie.get("ideon_session")
        return session.value if session is not None else None

    def _trusted_host(self):
        host = self.headers.get("Host", "").strip().lower()
        if not host:
            return False
        expected_hosts = {
            f"127.0.0.1:{self.server.server_port}",
            f"localhost:{self.server.server_port}",
            f"[::1]:{self.server.server_port}",
        }
        return host in expected_hosts

    def _auth_page(self, setup=False, error="", status=200):
        if setup:
            title = "ساخت حساب | IdeaVault"
            heading = "ساخت حساب IdeaVault"
            hint = "اولین اجرای برنامه است؛ نام کاربری و رمز عبور حساب‌تان را بسازید."
            action = "/setup"
            autocomplete = "new-password"
            confirmation = '<label for="password-confirm">تکرار رمز عبور</label><div class="password-field"><input id="password-confirm" name="password_confirm" type="password" maxlength="1024" autocomplete="new-password" required /><button class="password-toggle" type="button" aria-label="نمایش رمز عبور" aria-pressed="false" aria-controls="password-confirm"></button></div>'
            button = "ثبت‌نام و ورود"
            recovery_email = '<label for="email">ایمیل بازیابی</label><input id="email" name="email" type="email" maxlength="255" autocomplete="email" placeholder="you@example.com" required />'
        else:
            title = "ورود | IdeaVault"
            heading = "ورود به حساب"
            hint = "برای ادامه، نام کاربری و رمز عبور را وارد کنید."
            action = "/login"
            autocomplete = "current-password"
            confirmation = ""
            button = "ورود"
            recovery_email = ""
        page = LOGIN_HTML
        for placeholder, value in (
            ("{{TITLE}}", title),
            ("{{EYEBROW}}", "ثبت‌نام اولیه" if setup else "IdeaVault"),
            ("{{HEADING}}", heading),
            ("{{HINT}}", hint),
            ("{{ACTION}}", action),
            ("{{PASSWORD_AUTOCOMPLETE}}", autocomplete),
            ("{{CONFIRMATION}}", confirmation),
            ("{{EMAIL_FIELD}}", recovery_email),
            ("{{SIGNUP_LINK}}", "" if setup else '<div class="auth-switch"><a class="inline-link" href="/setup">ثبت‌نام در IdeaVault</a></div>'),
            ("{{RESET_ACCOUNT_LINK}}", "" if setup else '<div class="auth-switch"><a class="inline-link" href="/reset-account">حذف حساب ذخیره‌شده و ساخت حساب جدید</a></div>'),
            ("{{FORGOT_PASSWORD}}", "" if setup else '<button class="forgot-password" type="button" id="forgot-password">رمز عبور را فراموش کرده‌اید؟</button><dialog class="recovery-dialog" id="recovery-dialog" aria-labelledby="recovery-title"><h2 id="recovery-title">بازیابی رمز عبور</h2><form method="post" action="/recover"><p>برای فعال‌سازی بازیابی ایمیلی، ایمیل ثبت‌شده را وارد کنید. کد بازیابی به‌صورت محلی برای همین دستگاه تولید می‌شود.</p><label for="recovery-email">ایمیل ثبت‌شده</label><input id="recovery-email" name="email" type="email" maxlength="255" autocomplete="email" required /><button class="recovery-submit" type="submit">ارسال کد بازیابی</button></form><button class="recovery-close" type="button" id="recovery-close">متوجه شدم</button></dialog>'),
            ("{{ERROR}}", error),
            ("{{BUTTON}}", button),
        ):
            page = page.replace(placeholder, value)
        self._send_html(page, status=status)

    def _start_session(self):
        session = secrets.token_urlsafe(32)
        self.active_sessions.add(session)
        self._redirect("/", f"ideon_session={session}; Path=/; HttpOnly; SameSite=Strict")

    def _recovery_page(self, message="", error="", status=200):
        if not self.credentials:
            self._redirect("/setup")
            return
        safe_message = message if message else "برای بازنشانی رمز عبور، کد بازیابی را وارد کنید."
        content = f'''<!DOCTYPE html>
<html lang="fa" dir="rtl">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>بازیابی رمز عبور | IdeaVault</title>
  <style>
    * {{ box-sizing: border-box; }}
    body {{ margin: 0; min-height: 100vh; display: grid; place-items: center; padding: 24px; font-family: "Vazirmatn", Tahoma, sans-serif; background: radial-gradient(ellipse at 78% 100%, rgba(133,31,110,.42), transparent 42%), radial-gradient(ellipse at 8% 12%, rgba(81,42,112,.2), transparent 36%), #160d25; color: #f8f3ff; }}
    .card {{ width: min(100%, 540px); padding: 30px 28px 28px; border-radius: 30px; background: rgba(20,12,34,.32); border: 1px solid rgba(211,174,229,.16); box-shadow: 0 28px 90px rgba(8,3,18,.22), inset 0 1px 0 rgba(255,255,255,.03); }}
    h1 {{ margin: 0 0 14px; font-size: 30px; text-align: center; }}
    .message-box {{ margin: 0 0 18px; padding: 16px 14px; border: 1px solid rgba(211,174,229,.22); border-radius: 16px; background: rgba(14,8,26,.52); color: #f2d8ff; line-height: 1.9; text-align: center; font-size: 14px; }}
    .message-box strong {{ color: #fff; font-weight: 800; }}
    label {{ display: block; margin: 14px 0 7px; color: #e6dceb; font-size: 14px; font-weight: 700; }}
    input {{ width: 100%; height: 52px; padding: 0 16px; border: 1px solid rgba(205,174,221,.17); border-radius: 14px; color: #fbf7ff; background: rgba(14,8,26,.52); font: inherit; transition: border-color .2s, box-shadow .2s; }}
    input:focus {{ border-color: #b44ce1; outline: 0; box-shadow: 0 0 0 3px rgba(184,70,225,.15); }}
    .error {{ margin: 12px 0 0; color: #ff8998; font-size: 13px; text-align: center; }}
    button {{ width: 100%; min-height: 54px; margin-top: 18px; border: 0; border-radius: 14px; color: #fff; background: linear-gradient(105deg, #8751f2 0%, #cb35df 100%); box-shadow: 0 9px 24px rgba(153,56,213,.17); font: inherit; font-weight: 700; cursor: pointer; transition: transform .2s ease, filter .2s ease; }}
    button:hover {{ transform: translateY(-1px); filter: brightness(1.08); }}
    .back-to-login {{ display: flex; align-items: center; justify-content: center; gap: 9px; width: fit-content; min-height: 46px; margin: 18px auto 0; padding: 0 18px; border: 1px solid rgba(211,174,229,.24); border-radius: 14px; color: #ead7ff; background: linear-gradient(135deg, rgba(129,83,169,.2), rgba(255,255,255,.045)); box-shadow: 0 5px 16px rgba(8,3,18,.14), inset 0 1px 0 rgba(255,255,255,.07); font-size: 14px; font-weight: 700; text-decoration: none; transition: transform .2s ease, border-color .2s ease, background .2s ease, box-shadow .2s ease; }}
    .back-to-login:hover {{ transform: translateY(-1px); border-color: rgba(218,163,244,.48); color: #fff; background: linear-gradient(135deg, rgba(153,83,190,.3), rgba(255,255,255,.07)); box-shadow: 0 8px 20px rgba(8,3,18,.2), inset 0 1px 0 rgba(255,255,255,.1); }}
    .back-to-login:focus-visible {{ outline: 2px solid #c55aec; outline-offset: 3px; }}
    .back-to-login svg {{ width: 18px; height: 18px; }}
  </style>
</head>
<body>
  <main class="card">
    <h1>بازیابی رمز عبور</h1>
    <div class="message-box">{safe_message}</div>
    {error}
    <form method="post" action="/reset">
      <input type="hidden" name="email" value="{html.escape(self.credentials['email'])}" />
      <label for="code">کد بازیابی</label>
      <input id="code" name="code" type="text" maxlength="12" placeholder="کد ۶ رقمی" required />
      <label for="reset-password">رمز عبور جدید</label>
      <input id="reset-password" name="password" type="password" maxlength="1024" autocomplete="new-password" required />
      <label for="reset-password-confirm">تکرار رمز عبور جدید</label>
      <input id="reset-password-confirm" name="password_confirm" type="password" maxlength="1024" autocomplete="new-password" required />
      <button type="submit">تغییر رمز عبور</button>
    </form>
    <a class="back-to-login" href="/login"><span>بازگشت به ورود</span><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" aria-hidden="true"><path d="M19 12H5m0 0 7 7m-7-7 7-7"/></svg></a>
  </main>
</body>
</html>'''
        self._send_html(content, status=status)

    def do_GET(self):
        if not self._trusted_host():
            self.send_error(403)
            return
        path = urlsplit(self.path).path
        if path == "/reset-account":
            self._reset_account()
            self._redirect("/setup")
            return
        if path == "/login":
            if self._has_session():
                self._redirect("/")
            else:
                self._auth_page()
            return
        if path == "/setup":
            if self.credentials is None:
                self._auth_page(setup=True)
            else:
                self._redirect("/login")
            return
        if path == "/recover":
            self._redirect("/login")
            return
        if path != "/":
            self.send_error(404)
            return
        if self._has_session():
            self._send_html(self.page_html)
        else:
            self._redirect("/login")

    def do_POST(self):
        if not self._trusted_host():
            self.send_error(403)
            return
        path = urlsplit(self.path).path
        if path == "/logout":
            session = self._session_id()
            if session in self.active_sessions:
                self.active_sessions.remove(session)
            self._redirect("/login", "ideon_session=; Path=/; HttpOnly; SameSite=Strict; Max-Age=0")
            return
        if path == "/reset-account":
            self._reset_account()
            self._redirect("/setup", "ideon_session=; Path=/; HttpOnly; SameSite=Strict; Max-Age=0")
            return
        try:
            content_length = int(self.headers.get("Content-Length", "0"))
        except ValueError:
            self.send_error(400)
            return
        if content_length < 0 or content_length > 4096:
            self.send_error(400)
            return
        form = parse_qs(self.rfile.read(content_length).decode("utf-8", errors="replace"), keep_blank_values=True)
        if path == "/recover":
            if self.credentials is None:
                self._redirect("/setup")
                return
            email = normalize_email(form.get("email", [""])[0])
            if not email:
                self._auth_page(error='<p class="error" role="alert">ایمیل ثبت‌شده را وارد کنید.</p>', status=400)
                return
            if email != self.credentials.get("email", ""):
                self._auth_page(error='<p class="error" role="alert">ایمیل واردشده با حساب ثبت‌شده مطابقت ندارد.</p>', status=401)
                return
            code = str(secrets.randbelow(900000) + 100000)
            type(self).pending_recovery = {"email": email, "code": code, "expires_at": time.time() + EMAIL_RECOVERY_CODE_TTL}
            email_sent = send_recovery_email(email, code)
            if email_sent:
                message = f"کد بازیابی برای <strong>{html.escape(email)}</strong> ارسال شد. این کد فقط برای {EMAIL_RECOVERY_CODE_TTL // 60} دقیقه معتبر است."
            else:
                message = f"کد بازیابی برای <strong>{html.escape(email)}</strong> در این دستگاه ایجاد شد و در خروجی کنسول ثبت شد. برای ارسال واقعی، متغیرهای SMTP را تنظیم کنید."
            self._recovery_page(message=message, status=200)
            return
        if path == "/reset":
            if self.credentials is None:
                self._redirect("/setup")
                return
            email = normalize_email(form.get("email", [""])[0])
            code = form.get("code", [""])[0].strip()
            password = form.get("password", [""])[0]
            password_confirm = form.get("password_confirm", [""])[0]
            pending = type(self).pending_recovery
            if pending is None or time.time() > pending["expires_at"] or pending["email"] != email or pending["code"] != code:
                self._recovery_page(message="کد بازیابی نامعتبر یا منقضی شده است. دوباره درخواست جدید بدهید.", status=401, error='<div class="error" role="alert">کد بازیابی نامعتبر یا منقضی شده است.</div>')
                return
            if len(password) < 8:
                self._recovery_page(message=f"کد بازیابی برای <strong>{html.escape(email)}</strong> درست است؛ فقط رمز جدید را تنظیم کنید.", status=400, error='<div class="error" role="alert">رمز عبور باید حداقل ۸ حرف باشد.</div>')
                return
            if password != password_confirm:
                self._recovery_page(message=f"کد بازیابی برای <strong>{html.escape(email)}</strong> درست است؛ فقط رمز جدید را تنظیم کنید.", status=400, error='<div class="error" role="alert">تکرار رمز عبور با رمز جدید یکسان نیست.</div>')
                return
            try:
                credentials = create_credentials(self.credentials_path, self.credentials["username"], password, email)
            except OSError:
                self._recovery_page(message=f"کد بازیابی برای <strong>{html.escape(email)}</strong> درست است، اما ذخیره‌سازی انجام نشد.", status=500, error='<div class="error" role="alert">ذخیره حساب انجام نشد؛ دسترسی پوشه را بررسی کنید.</div>')
                return
            type(self).credentials = credentials
            type(self).pending_recovery = None
            self._redirect("/login")
            return
        if path not in ("/login", "/setup"):
            self.send_error(404)
            return
        setup = path == "/setup"
        if setup and self.credentials is not None:
            self._redirect("/login")
            return
        if not setup and self.credentials is None:
            self._redirect("/setup")
            return
        username = normalize_username(form.get("username", [""])[0])
        password = form.get("password", [""])[0]
        if setup:
            email = normalize_email(form.get("email", [""])[0])
            if not username or len(username) > 80:
                error = '<p class="error" role="alert">نام کاربری را وارد کنید (حداکثر ۸۰ حرف).</p>'
            elif not email:
                error = '<p class="error" role="alert">ایمیل بازیابی را وارد کنید.</p>'
            elif len(password) < 8:
                error = '<p class="error" role="alert">رمز عبور باید حداقل ۸ حرف باشد.</p>'
            elif password != form.get("password_confirm", [""])[0]:
                error = '<p class="error" role="alert">تکرار رمز عبور با رمز یکسان نیست.</p>'
            else:
                try:
                    credentials = create_credentials(self.credentials_path, username, password, email)
                except OSError:
                    error = '<p class="error" role="alert">ذخیره حساب انجام نشد؛ دسترسی پوشه را بررسی کنید.</p>'
                    self._auth_page(setup=True, error=error, status=500)
                    return
                type(self).credentials = credentials
                self._start_session()
                return
            self._auth_page(setup=True, error=error, status=400)
            return
        credentials = self.credentials
        username_matches = hmac.compare_digest(username.encode("utf-8"), credentials["username"].encode("utf-8"))
        password_hash = hashlib.pbkdf2_hmac(
            "sha256", password.encode("utf-8"), credentials["salt"], PASSWORD_HASH_ROUNDS
        )
        if username_matches and hmac.compare_digest(password_hash, credentials["password_hash"]):
            self._start_session()
            return
        error = '<p class="error" role="alert">نام کاربری یا رمز عبور نادرست است.</p>'
        self._auth_page(error=error, status=401)


def hide_console_window():
    if os.name != "nt":
        return
    try:
        import ctypes
        hwnd = ctypes.windll.kernel32.GetConsoleWindow()
        if hwnd:
            ctypes.windll.user32.ShowWindow(hwnd, 0)
    except (AttributeError, OSError, ValueError):
        pass


def main():
    jalali_today = gregorian_to_jalali(date.today())
    today_label = "%04d/%02d/%02d" % jalali_today
    today_label = today_label.translate(
        str.maketrans("0123456789", "۰۱۲۳۴۵۶۷۸۹")
    )
    page_html = HTML.replace("امروز", today_label)
    page_html = page_html.replace("<span>IdeaVault</span>", "")
    page_html = page_html.replace("IdeaVault | ", "")
    page_html = page_html.replace("دیروز", today_label)
    page_html = page_html.replace("پرامپت طراحی:", "ایده بعدی از همین‌جا شروع می‌شود")
    page_html = page_html.replace(
        "بخش‌های مشخص‌شده با طراحی جدید و بخش لیست ایده‌ها با ظاهری مدرن، تمیز و مینیمال طراحی شدند.",
        "هر ایده می‌تواند شروع یک مسیر تازه باشد؛ آن را ثبت کن تا فراموش نشود."
    )
    page_html = page_html.replace(
        "کارت‌ها، فیلدها، چیپ‌ها و دکمه‌ها با Border ظریف، Shadow نرم و رنگ‌بندی بنفش ملایم طراحی شده‌اند\n          تا تجربه‌ای شبیه یک محصول SaaS حرفه‌ای ایجاد شود",
        "ایده‌هایت را جمع کن، پرورش بده و در زمان مناسب به آن‌ها برگرد"
    )
    page_html = page_html.replace("</body>", AUTH_SCRIPT)

    IdeaVaultHandler.page_html = page_html
    IdeaVaultHandler.credentials_path = get_credentials_path()
    IdeaVaultHandler.credentials = load_credentials(IdeaVaultHandler.credentials_path)
    IdeaVaultHandler.active_sessions = set()
    server = ThreadingHTTPServer(("127.0.0.1", 0), IdeaVaultHandler)
    login_path = "/login"
    url = f"http://127.0.0.1:{server.server_port}{login_path}"
    hide_console_window()
    webbrowser.open(url)
    print(f"IdeaVault is running at {url}. Press Ctrl+C to stop.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()

if __name__ == "__main__":
    main()
