#!/bin/bash

echo "🔄 Исправление Android v2 embedding для Syndi Mobile"

# 1. Обновляем AndroidManifest.xml
echo "📝 Обновляем AndroidManifest.xml..."
cat > android/app/src/main/AndroidManifest.xml << 'EOF'
<manifest xmlns:android="http://schemas.android.com/apk/res/android">
    <uses-permission android:name="android.permission.INTERNET"/>
    
    <application
        android:label="Syndi AI"
        android:name="${applicationName}"
        android:icon="@mipmap/ic_launcher"
        android:usesCleartextTraffic="true"
        android:allowBackup="true"
        android:theme="@style/LaunchTheme">
        
        <activity
            android:name=".MainActivity"
            android:exported="true"
            android:launchMode="singleTop"
            android:theme="@style/LaunchTheme"
            android:configChanges="orientation|keyboardHidden|keyboard|screenSize|smallestScreenSize|locale|layoutDirection|fontScale|screenLayout|density|uiMode"
            android:hardwareAccelerated="true"
            android:windowSoftInputMode="adjustResize">
            
            <intent-filter>
                <action android:name="android.intent.action.MAIN"/>
                <category android:name="android.intent.category.LAUNCHER"/>
            </intent-filter>
        </activity>
        
        <meta-data
            android:name="flutterEmbedding"
            android:value="2"/>
    </application>
</manifest>
EOF

# 2. Обновляем MainActivity.kt
echo "📝 Обновляем MainActivity.kt..."
cat > android/app/src/main/kotlin/com/syndi/mobile/MainActivity.kt << 'EOF'
package com.syndi.mobile

import io.flutter.embedding.android.FlutterActivity

class MainActivity: FlutterActivity()
EOF

# 3. Обновляем app/build.gradle
echo "📝 Обновляем app/build.gradle..."
cat > android/app/build.gradle << 'EOF'
def localProperties = new Properties()
def localPropertiesFile = rootProject.file('local.properties')
if (localPropertiesFile.exists()) {
    localPropertiesFile.withReader('UTF-8') { reader ->
        localProperties.load(reader)
    }
}

def flutterRoot = localProperties.getProperty('flutter.sdk')
if (flutterRoot == null) {
    throw new GradleException("Flutter SDK not found. Define location with flutter.sdk in the local.properties file.")
}

def flutterVersionCode = localProperties.getProperty('flutter.versionCode')
if (flutterVersionCode == null) {
    flutterVersionCode = '1'
}

def flutterVersionName = localProperties.getProperty('flutter.versionName')
if (flutterVersionName == null) {
    flutterVersionName = '1.0'
}

apply plugin: 'com.android.application'
apply plugin: 'kotlin-android'
apply from: "$flutterRoot/packages/flutter_tools/gradle/flutter.gradle"

android {
    compileSdkVersion 34
    ndkVersion flutter.ndkVersion

    compileOptions {
        sourceCompatibility JavaVersion.VERSION_1_8
        targetCompatibility JavaVersion.VERSION_1_8
    }

    kotlinOptions {
        jvmTarget = '1.8'
    }

    sourceSets {
        main.java.srcDirs += 'src/main/kotlin'
    }

    defaultConfig {
        applicationId "com.syndi.mobile"
        minSdkVersion 21
        targetSdkVersion 34
        versionCode flutterVersionCode.toInteger()
        versionName flutterVersionName
    }

    buildTypes {
        release {
            signingConfig signingConfigs.debug
            minifyEnabled false
        }
    }
}

flutter {
    source '../..'
}

dependencies {
    implementation "org.jetbrains.kotlin:kotlin-stdlib-jdk7:$kotlin_version"
}
EOF

# 4. Обновляем pubspec.yaml
echo "📝 Обновляем pubspec.yaml..."
cat > pubspec.yaml << 'EOF'
name: syndi_mobile
description: Syndi AI - мобильное приложение
publish_to: 'none'
version: 1.0.0+1

environment:
  sdk: '>=3.0.0 <4.0.0'

dependencies:
  flutter:
    sdk: flutter
  cupertino_icons: ^1.0.6
  provider: ^6.1.1
  shared_preferences: ^2.2.2
  dio: ^5.4.0
  intl: ^0.18.1

dev_dependencies:
  flutter_test:
    sdk: flutter
  flutter_lints: ^3.0.1

flutter:
  uses-material-design: true
EOF

# 5. Очистка
echo "🧹 Очистка проекта..."
flutter clean
rm -rf .dart_tool build pubspec.lock

# 6. Получение зависимостей
echo "📦 Установка зависимостей..."
flutter pub get

# 7. Попытка сборки
echo "🔨 Попытка сборки debug APK..."
flutter build apk --debug

if [ $? -eq 0 ]; then
    echo "✅ Сборка успешна! APK находится в:"
    ls -la build/app/outputs/flutter-apk/app-debug.apk
    
    echo "🔨 Пробуем release сборку..."
    flutter build apk --release
else
    echo "❌ Ошибка сборки. Запускаю диагностику..."
    flutter doctor -v
    echo "Пожалуйста, покажите этот вывод"
fi
EOF

chmod +x fix_v2_embedding.sh
./fix_v2_embedding.sh
