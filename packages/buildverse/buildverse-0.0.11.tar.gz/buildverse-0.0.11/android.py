import os
import pathlib
import shutil
import subprocess
import sys
from typing import Optional

import cmake
import configenv
import externaltools
import generator

IMAGES = {}


class AndroidGeneratorError(Exception):
    pass


class AndroidAppHandler(cmake.Handler):
    def __init__(self, srcdir: pathlib.Path, builddir: Optional[pathlib.Path] = None, **kargs: any):
        super().__init__("android", srcdir, builddir)
        self.android_workspace = self.get_build_root_dir() / "android"
        self.gradle_workspace = self.android_workspace / "gradle"
        self.studio_workspace = self.android_workspace / "studio"
        self.gradle_workspace.mkdir(exist_ok=True, parents=True)
        self.studio_workspace.mkdir(exist_ok=True, parents=True)
        self.toolchain = externaltools.init_toolchain("android")
        self.gradle_exe = externaltools.acquire_tool("gradle")
        self.extra_args = kargs

    def get_permission_map(self) -> dict[str, str]:
        return {}

    def _generate_appx_manifest_xml(self, gen: generator.Generator, config: dict[str:object]) -> None:
        manifestfilepath = "app/src/main/AndroidManifest.xml"
        manifesttemplate = """<?xml version="1.0" encoding="utf-8"?>
<manifest xmlns:android="http://schemas.android.com/apk/res/android"
    android:versionCode="{version_code}"
    android:versionName="{version_full}"
> {permissionxml} <application
        android:allowBackup="true"
        android:icon="@mipmap/ic_launcher"
        android:label="@string/app_name"
        android:supportsRtl="true"
        android:usesCleartextTraffic="true"
        android:theme="@style/AppTheme">
        <activity
            android:name=".MainActivity"
            android:launchMode="singleTask"
            android:exported="true"
            android:configChanges="orientation|screenSize">
            <intent-filter>
                <action android:name="android.intent.action.MAIN" />
                <category android:name="android.intent.category.LAUNCHER" />
                {usb_intent_filter}
            </intent-filter>
            {usb_device_metadata}
        </activity>
        {navigation_svc}
    </application>
</manifest>
        """
        permission_map = {
            "internet": '<uses-permission android:name="android.permission.INTERNET"/>\n',
            "bluetooth": '<uses-permission android:name="android.permission.BLUETOOTH"/>\n',
            "in-app-purchases": '<uses-permission android:name="com.android.vending.BILLING" />\n',
            "ble-server": '<uses-permission android:name="android.permission.BLUETOOTH_SCAN"/>\n'
            '<uses-permission android:name="android.permission.BLUETOOTH_CONNECT"/>\n'
            '<uses-permission android:name="android.permission.BLUETOOTH_ADVERTISE"/>\n',
            "location": '<uses-permission android:name="android.permission.ACCESS_FINE_LOCATION"/>\n'
            '<uses-permission android:name="android.permission.ACCESS_COARSE_LOCATION"/>\n',
            "navigation": '<uses-permission android:name="android.permission.FOREGROUND_SERVICE_LOCATION"/>\n'
            # '<uses-permission android:name="android.permission.ACCESS_BACKGROUND_LOCATION"/>\n' # Google is strict about this
            '<uses-permission android:name="android.permission.FOREGROUND_SERVICE"/>\n',
            #"gyroscope": '<uses-permission android:name="android.permission.ACTIVITY_RECOGNITION"/>\n',
            "gyroscope": "",
            "usb": "",
            "extended-execution": '<uses-permission android:name="android.permission.POST_NOTIFICATIONS"/>\n'
            '<uses-permission android:name="android.permission.WAKE_LOCK"/>\n',
        }

        formatvars = {
            "usb_intent_filter": "",
            "usb_device_metadata": "",
            "version_code": config["build"]["VersionCode"],
            "version_full": config["build"]["VersionFull"],
        }
        permissionxml = ""
        usb_intent_filter = ""
        usb_device_metadata = ""
        navigation_svc = ""
        app_config: dict[str, object] = config["application"]
        permissions: set[str] = set(filter(None, app_config.get("permissions", "").split(",")))
        usb_devices: set[str] = set(filter(None, app_config.get("usb-devices", "").split(",")))
        for permission in permissions:
            permissionxml += permission_map[permission]
        if "usb" in permissions:
            if not usb_devices:
                raise AndroidGeneratorError(f"Cannot find Usb-Devices in manifest. Found {app_config.keys()}")
            usb_intent_filter = '<action android:name="android.hardware.usb.action.USB_DEVICE_ATTACHED" />'
            usb_device_metadata = (
                '<meta-data android:name="android.hardware.usb.action.USB_DEVICE_ATTACHED" ' + 'android:resource="@xml/device_filter" />'
            )
            usb_device_filter_file_path = "app/src/main/res/xml/device_filter.xml"
            usb_device_filter_file_contents = '<?xml version="1.0" encoding="utf-8"?><resources>\n'
            for device_spec in usb_devices:
                vid, pid = device_spec.split(":")
                usb_device_filter_file_contents += f'<usb-device vendor-id="0x{vid}" product-id="0x{pid}"/>\n'
            usb_device_filter_file_contents += "</resources>\n"
            gen.GenerateFileWithContents(usb_device_filter_file_path, usb_device_filter_file_contents)
        if "navigation" in permissions:
            navigation_svc = '<service android:name=".LocationForegroundService" android:foregroundServiceType="location" />'

        formatvars["permissionxml"] = permissionxml
        formatvars["usb_intent_filter"] = usb_intent_filter
        formatvars["usb_device_metadata"] = usb_device_metadata
        formatvars["navigation_svc"] = navigation_svc
        manifestcontent = manifesttemplate.format(**formatvars)
        gen.GenerateFileWithContents(manifestfilepath, manifestcontent)

    def generate(self, *_args: str) -> None:
        for name, configfile in self.get_app_manifests().items():
            bdir = self.android_workspace / name
            print( self.toolchain)
            gen, config = self.generate_build_dir_for_manifest(
                name,
                configfile,
                bdir,
                bindings={
                    "AndroidNDKPath": self.toolchain["ndk"].as_posix(),
                    "AndroidNDKVersion": self.toolchain["ndk_version"],
                    "AndroidSDKPath": str(self.toolchain["sdk_root"]),
                    "AndroidSDKVersion": str(self.toolchain["sdk_version"]),
                },
            )
            self._generate_appx_manifest_xml(gen, config)
            self._run(bdir, [self.gradle_exe.as_posix(), "wrapper"])

    def _run(self, builddir: pathlib.Path, cmd: list[str], **kwargs: str) -> None:
        runenv = self.toolchain["environ"]
        cmakeexe = externaltools.get_cmake()
        runenv["PATH"] += os.pathsep + cmakeexe.parent.as_posix() + os.pathsep + externaltools.get_ninja().parent.as_posix()
        subprocess.check_call(cmd, cwd=str(builddir), env=runenv, **kwargs)

    def build(self, *_args: str) -> None:
        for name in self.get_app_manifests():
            bdir = self.android_workspace / name
            gradlew = "gradlew.bat" if sys.platform == "win32" else "gradlew"
            self._run(bdir, [(bdir / gradlew).as_posix(), "assembleRelease", "--info"])

    def package(self, *_args: str) -> None:
        for name in self.get_app_manifests():
            bdir = self.android_workspace / name
            gradlew = "gradlew.bat" if sys.platform == "win32" else "gradlew"
            self._run(bdir,[(bdir / gradlew).as_posix(), "assembleRelease", "bundleRelease", "--info"])
            bundlefile = bdir / "app" / "build" / "outputs" / "bundle" / "release" / "app-release.aab"
            if not bundlefile.exists():
                raise AndroidGeneratorError(f"Cannot find {bundlefile}")
            storepass = configenv.ConfigEnv(str(self.get_source_dir())).GetConfigStr("ANDROID_KEYSTORE_PASS")
            keystore = configenv.ConfigEnv(str(self.get_source_dir())).GetConfigPath("ANDROID_KEYSTORE_FILE").as_posix()
            self._run(
                bdir,
                [
                    self.toolchain["jarsigner"].as_posix(),
                    "-verbose",
                    "-sigalg",
                    "SHA256withRSA",
                    "-digestalg",
                    "SHA-256",
                    "-keystore",
                    keystore,
                    "-storepass",
                    storepass,
                    bundlefile.as_posix(),
                    "key0",
                ],
            )

    def clean(self, *_args: str) -> None:
        if sys.platform == "linux":
            os.system("killall -15 java")  # noqa: S605, S607
        elif sys.platform == "win32":
            os.system("taskkill /F /IM java.exe")  # noqa: S605, S607
        else:
            pass
        subprocess.run([str(shutil.which("adb", path=(self.toolchain["sdk_root"] / "platform-tools").as_posix())), "emu", "kill"], check=False)
        bdir = self.android_workspace
        for name in self.get_app_manifests():
            if (bdir / name).is_dir():
                self.rmtree(bdir / name)

    def open(self, *_args: str) -> None:
        for name in self.get_app_manifests():
            bdir = self.android_workspace / name
            self._run(bdir, [self.toolchain["studio"].as_posix(), bdir.as_posix()], close_fds=True)


class AndroidCLIHandler(cmake.CMakeHandler):
    def __init__(self, srcdir: pathlib.Path, builddir: Optional[pathlib.Path] = None, **kargs: any):
        super().__init__("andcli", srcdir, builddir, **kargs)
        self.toolchain = externaltools.init_toolchain("android")

    def get_generator(self)-> str:
        return "Ninja"

    def get_generator_args(self, arch: str, _config: str) -> list[str]:
        archmapping = {"arm": "armeabi-v7a", "arm64": "arm64-v8a"}
        return [
            "-DANDROID=1",
            "-DANDROID_NATIVE_API_LEVEL=28",
            f"-DCMAKE_TOOLCHAIN_FILE={self.toolchain["cmake_toolchain_file"].as_posix()}",
            "-DANDROID_ABI=" + archmapping[arch],
        ]
