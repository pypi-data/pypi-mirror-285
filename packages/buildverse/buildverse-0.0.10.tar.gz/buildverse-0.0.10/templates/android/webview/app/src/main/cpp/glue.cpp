#include "native_glue_export.h"

#define WEBVIEW_APP_EXPORT JNIEXPORT

#include "webview_app.h"

#include <android/log.h>
#include <cinttypes>
#include <cstring>
#include <jni.h>

// #define LOGI(...) ((void)__android_log_print(ANDROID_LOG_INFO, "android-webview-glue::", __VA_ARGS__))

struct GlobalState
{
    JavaVM*   vm                                                = nullptr;
    JNIEnv*   env                                               = nullptr;
    jclass    jcls_MainActivity                                 = nullptr;
    jmethodID jmtd_MainActivity_onStartForegroundLocationUpdate = nullptr;
    jmethodID jmtd_MainActivity_onStopForegroundLocationUpdate  = nullptr;
    jmethodID jmtd_MainActivity_onStartOrientationUpdate        = nullptr;
    jmethodID jmtd_MainActivity_onStopOrientationUpdate         = nullptr;
    jmethodID jmtd_MainActivity_onStartLocationUpdate           = nullptr;
    jmethodID jmtd_MainActivity_onStopLocationUpdate            = nullptr;
    jmethodID jmtd_MainActivity_onRequestIAPInit                = nullptr;
    jmethodID jmtd_MainActivity_onRequestIAPFeature             = nullptr;

    bool location_request_status            = false;
    bool location_foreground_request_status = false;
    bool orientation_request_status         = false;
};

static GlobalState s_g;

static void jni_initvm(JNIEnv* env)
{
    if (s_g.vm == nullptr) { env->GetJavaVM(&s_g.vm); }
    if (s_g.env == nullptr) { s_g.env = env; }
    if (s_g.jcls_MainActivity == nullptr)
    {
        s_g.jcls_MainActivity = env->FindClass("com/zzzsAndroid.AppPackageNamezzze/MainActivity");
        s_g.jmtd_MainActivity_onStopForegroundLocationUpdate
            = env->GetStaticMethodID(s_g.jcls_MainActivity, "cbStopForegroundLocationUpdate", "()V");
        s_g.jmtd_MainActivity_onStartForegroundLocationUpdate
            = env->GetStaticMethodID(s_g.jcls_MainActivity, "cbStartForegroundLocationUpdate", "()V");
        s_g.jmtd_MainActivity_onStopOrientationUpdate  = env->GetStaticMethodID(s_g.jcls_MainActivity, "cbStopOrientationUpdate", "()V");
        s_g.jmtd_MainActivity_onStartOrientationUpdate = env->GetStaticMethodID(s_g.jcls_MainActivity, "cbStartOrientationUpdate", "()V");
        s_g.jmtd_MainActivity_onStopLocationUpdate     = env->GetStaticMethodID(s_g.jcls_MainActivity, "cbStopLocationUpdate", "()V");
        s_g.jmtd_MainActivity_onStartLocationUpdate    = env->GetStaticMethodID(s_g.jcls_MainActivity, "cbStartLocationUpdate", "()V");
        s_g.jmtd_MainActivity_onRequestIAPInit = env->GetStaticMethodID(s_g.jcls_MainActivity, "cbRequestIAPInit", "(Ljava/lang/String;)V");
        s_g.jmtd_MainActivity_onRequestIAPFeature
            = env->GetStaticMethodID(s_g.jcls_MainActivity, "cbRequestIAPFeature", "(Ljava/lang/String;)V");
        s_g.jcls_MainActivity = reinterpret_cast<jclass>(env->NewGlobalRef(s_g.jcls_MainActivity));
    }
}
static JNIEnv* jnienv()
{
    JNIEnv* env;
    if (s_g.vm == nullptr) return nullptr;
    int status = s_g.vm->GetEnv(reinterpret_cast<void**>(&env), JNI_VERSION_1_6);
    if (status == JNI_EDETACHED)
    {
        JavaVMAttachArgs thr_args = {.version = JNI_VERSION_1_6, .name = nullptr, .group = nullptr};
        s_g.vm->AttachCurrentThread(&env, &thr_args);
    }
    return env;
}

static void request_iap_init(const char* name)
{
    jstring jstr = jnienv()->NewStringUTF(name);
    jnienv()->CallStaticVoidMethod(s_g.jcls_MainActivity, s_g.jmtd_MainActivity_onRequestIAPInit, jstr);
}

static void request_iap_feature(const char* name)
{
    jstring jstr = jnienv()->NewStringUTF(name);
    jnienv()->CallStaticVoidMethod(s_g.jcls_MainActivity, s_g.jmtd_MainActivity_onRequestIAPFeature, jstr);
}

static void request_location_update_start()
{
    if (s_g.location_request_status) return;
    s_g.location_request_status = true;
    jnienv()->CallStaticVoidMethod(s_g.jcls_MainActivity, s_g.jmtd_MainActivity_onStartLocationUpdate);
}

static void request_location_update_stop()
{
    if (!s_g.location_request_status) return;
    s_g.location_request_status = false;
    jnienv()->CallStaticVoidMethod(s_g.jcls_MainActivity, s_g.jmtd_MainActivity_onStopLocationUpdate);
}

static void request_orientation_update_start()
{
    if (s_g.orientation_request_status) return;
    s_g.orientation_request_status = true;
    jnienv()->CallStaticVoidMethod(s_g.jcls_MainActivity, s_g.jmtd_MainActivity_onStartOrientationUpdate);
}

static void request_orientation_update_stop()
{
    if (!s_g.orientation_request_status) return;
    s_g.orientation_request_status = false;
    jnienv()->CallStaticVoidMethod(s_g.jcls_MainActivity, s_g.jmtd_MainActivity_onStopOrientationUpdate);
}

static void request_foreground_service_start()
{
    if (s_g.location_foreground_request_status) return;
    s_g.location_foreground_request_status = true;
    jnienv()->CallStaticVoidMethod(s_g.jcls_MainActivity, s_g.jmtd_MainActivity_onStartForegroundLocationUpdate);
}

static void request_foreground_service_stop()
{
    if (!s_g.location_foreground_request_status) return;
    s_g.location_foreground_request_status = false;
    jnienv()->CallStaticVoidMethod(s_g.jcls_MainActivity, s_g.jmtd_MainActivity_onStopForegroundLocationUpdate);
}

#pragma clang diagnostic push
#pragma clang diagnostic ignored "-Wmissing-prototypes"
#pragma clang diagnostic ignored "-Wunused-parameter"

extern "C" JNIEXPORT void JNICALL Java_com_zzzsAndroid.AppPackageNamezzze_MainActivity_glueAppInit(JNIEnv* env, jobject /*thiz*/)
{
    s_g = {};
    jni_initvm(env);
    app_callbacks callbacks{request_location_update_start,
                            request_location_update_stop,
                            request_orientation_update_start,
                            request_orientation_update_stop,
                            request_foreground_service_start,
                            request_foreground_service_stop,
                            request_iap_init,
                            request_iap_feature};
    app_init(&callbacks);
    android_app_init(env);
}

extern "C" JNIEXPORT void JNICALL Java_com_zzzsAndroid.AppPackageNamezzze_MainActivity_glueAppDestroy(JNIEnv* /*env*/, jobject /*thiz*/)
{
    // The process can still hang around due to life-cycle practices of android
    // The services are also sometimes stopped after MainActivity is Destroyed so be careful
    // Always reset s_g on init
    // TODO : its wierd to destroy and then decrement
    // Keep a count on glue and do a lazy destroy
    android_app_destroy();
    app_destroy();
    s_g = {};
}

extern "C" JNIEXPORT void JNICALL Java_com_zzzsAndroid.AppPackageNamezzze_MainActivity_glueAppActivityStart(JNIEnv* env, jobject /*thiz*/)
{
    jni_initvm(env);
    app_acquire_ref(1u);
    request_location_update_start();
    request_foreground_service_start();
    request_orientation_update_start();
}

extern "C" JNIEXPORT void JNICALL Java_com_zzzsAndroid.AppPackageNamezzze_MainActivity_glueAppActivityStop(JNIEnv* env, jobject /*thiz*/)
{
    jni_initvm(env);
    app_release_ref(1u);
}

extern "C" JNIEXPORT jstring JNICALL Java_com_zzzsAndroid.AppPackageNamezzze_MainActivity_glueGetWebserverUrl(JNIEnv* env, jobject /*thiz*/)
{
    jni_initvm(env);
    return env->NewStringUTF(get_webserver_url());
}

extern "C" JNIEXPORT void JNICALL Java_com_zzzsAndroid.AppPackageNamezzze_LocationForegroundService_glueUpdateLocation(JNIEnv* env,
                                                                                                                       jobject thiz,
                                                                                                                       jobject location)
{
    jni_initvm(env);
    android_update_location(env, thiz, location);
}

extern "C" JNIEXPORT void
    JNICALL Java_com_zzzsAndroid.AppPackageNamezzze_MainActivity_glueUpdateOrientation(JNIEnv* env, jobject thiz, jint orientation)
{
    jni_initvm(env);
    android_update_orientation(env, thiz, orientation);
}

extern "C" JNIEXPORT void JNICALL Java_com_zzzsAndroid.AppPackageNamezzze_BillingManager_glueIAPReset(JNIEnv* env, jobject /*thiz*/)
{
    jni_initvm(env);
    iap_reset();
}

extern "C" JNIEXPORT void JNICALL Java_com_zzzsAndroid.AppPackageNamezzze_BillingManager_glueIAPInitialized(JNIEnv* /*env*/,
                                                                                                            jobject /*thiz*/)
{}

extern "C" JNIEXPORT void JNICALL Java_com_zzzsAndroid.AppPackageNamezzze_BillingManager_glueIAPRequestFailed(JNIEnv* env,
                                                                                                              jobject /*thiz*/,
                                                                                                              jstring name,
                                                                                                              jint    code,
                                                                                                              jstring message)
{
    jni_initvm(env);
    iap_request_failed(env->GetStringUTFChars(name, nullptr), static_cast<uint32_t>(code), env->GetStringUTFChars(message, nullptr));
}

extern "C" JNIEXPORT void
    JNICALL Java_com_zzzsAndroid.AppPackageNamezzze_BillingManager_glueIAPAvailable(JNIEnv* env, jobject /*thiz*/, jstring name)
{
    jni_initvm(env);
    iap_available(env->GetStringUTFChars(name, nullptr));
}

extern "C" JNIEXPORT void
    JNICALL Java_com_zzzsAndroid.AppPackageNamezzze_LocationForegroundService_glueAppLocationServiceStarted(JNIEnv* env, jobject /*thiz*/)
{
    jni_initvm(env);
    app_acquire_ref(2u);
}

extern "C" JNIEXPORT void
    JNICALL Java_com_zzzsAndroid.AppPackageNamezzze_LocationForegroundService_glueAppLocationServiceStopped(JNIEnv* env, jobject /*thiz*/)
{
    jni_initvm(env);
    app_release_ref(2u);
}
#pragma clang diagnostic pop
