[app]
title = Hermez Link
package.name = hermezlink
package.domain = org.ps5homebrew
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,json
version = 1.0.0
requirements = python3,kivy==2.3.0,android

orientation = portrait
fullscreen = 0
android.permissions = INTERNET, READ_EXTERNAL_STORAGE, WRITE_EXTERNAL_STORAGE, MANAGE_EXTERNAL_STORAGE
android.api = 33
android.minapi = 26
android.sdk = 33
android.ndk = 25b
android.archs = arm64-v8a, armeabi-v7a

# Icon — replace icon.png with your own 512x512 image
icon.filename = %(source.dir)s/icon.png

[buildozer]
log_level = 2
warn_on_root = 1
