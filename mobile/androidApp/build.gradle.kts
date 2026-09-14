plugins {
    alias(libs.plugins.androidApplication)
    alias(libs.plugins.composeCompiler)
}

val productionApiBaseUrl =
    providers
        .gradleProperty("portfolioProductionApiBaseUrl")
        .orElse("https://production-api-not-configured.invalid/api/v1/")

android {
    namespace = "com.akahalu.portfolio"
    compileSdk = libs.versions.androidCompileSdk.get().toInt()

    defaultConfig {
        applicationId = "com.akahalu.portfolio"
        minSdk = libs.versions.androidMinSdk.get().toInt()
        targetSdk = libs.versions.androidTargetSdk.get().toInt()

        versionCode = 1
        versionName = "1.0.0"
    }

    buildTypes {
        debug {
            applicationIdSuffix = ".debug"
            versionNameSuffix = "-debug"

            buildConfigField(
                "String",
                "API_BASE_URL",
                "\"http://192.168.0.75:8000/api/v1/\"",
            )
        }

        release {
            isMinifyEnabled = true
            isShrinkResources = true

            buildConfigField(
                "String",
                "API_BASE_URL",
                "\"${productionApiBaseUrl.get()}\"",
            )

            proguardFiles(
                getDefaultProguardFile("proguard-android-optimize.txt"),
            )
        }
    }

    buildFeatures {
        buildConfig = true
    }
}

dependencies {
    implementation(project(":shared"))
    implementation(libs.androidx.activity.compose)
}