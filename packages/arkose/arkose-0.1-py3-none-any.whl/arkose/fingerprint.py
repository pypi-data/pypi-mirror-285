import random
import hashlib
import os
import base64
import uuid
from .murmur import murmur_hash

base_fingerprint = {
    "DNT": "unknown",
    "L": "en-US",
    "D": 24,
    "PR": 1,
    "S": [1920, 1200],
    "AS": [1920, 1200],
    "TO": 9999,
    "SS": True,
    "LS": True,
    "IDB": True,
    "B": False,
    "ODB": True,
    "CPUC": "unknown",
    "PK": "Win32",
    "CFP": f"canvas winding:yes~canvas fp:data:image/png;base64,{base64.b64encode(os.urandom(8)).decode()}",
    "FR": False,
    "FOS": False,
    "FB": False,
    "JSF": [
        "Andale Mono", "Arial", "Arial Black", "Arial Hebrew", "Arial MT", "Arial Narrow", 
        "Arial Rounded MT Bold", "Arial Unicode MS", "Bitstream Vera Sans Mono", "Book Antiqua", 
        "Bookman Old Style", "Calibri", "Cambria", "Cambria Math", "Century", "Century Gothic", 
        "Century Schoolbook", "Comic Sans", "Comic Sans MS", "Consolas", "Courier", "Courier New", 
        "Garamond", "Geneva", "Georgia", "Helvetica", "Helvetica Neue", "Impact", "Lucida Bright", 
        "Lucida Calligraphy", "Lucida Console", "Lucida Fax", "LUCIDA GRANDE", "Lucida Handwriting", 
        "Lucida Sans", "Lucida Sans Typewriter", "Lucida Sans Unicode", "Microsoft Sans Serif", 
        "Monaco", "Monotype Corsiva", "MS Gothic", "MS Outlook", "MS PGothic", "MS Reference Sans Serif", 
        "MS Sans Serif", "MS Serif", "MYRIAD", "MYRIAD PRO", "Palatino", "Palatino Linotype", 
        "Segoe Print", "Segoe Script", "Segoe UI", "Segoe UI Light", "Segoe UI Semibold", "Segoe UI Symbol", 
        "Tahoma", "Times", "Times New Roman", "Times New Roman PS", "Trebuchet MS", "Verdana", 
        "Wingdings", "Wingdings 2", "Wingdings 3",
    ],
    "P": [
        "Chrome PDF Plugin::Portable Document Format::application/x-google-chrome-pdf~pdf",
        "Chrome PDF Viewer::::application/pdf~pdf",
        "Native Client::::application/x-nacl~,application/x-pnacl~",
    ],
    "T": [0, False, False],
    "H": 24,
    "SWF": False,
}

languages = [
    "af", "af-ZA", "ar", "ar-AE", "ar-BH", "ar-DZ", "ar-EG", "ar-IQ", "ar-JO", "ar-KW", "ar-LB", "ar-LY", 
    "ar-MA", "ar-OM", "ar-QA", "ar-SA", "ar-SY", "ar-TN", "ar-YE", "az", "az-AZ", "be", "be-BY", "bg", 
    "bg-BG", "bs-BA", "ca", "ca-ES", "cs", "cs-CZ", "cy", "cy-GB", "da", "da-DK", "de", "de-AT", "de-CH", 
    "de-DE", "de-LI", "de-LU", "dv", "dv-MV", "el", "el-GR", "en", "en-AU", "en-BZ", "en-CA", "en-CB", 
    "en-GB", "en-IE", "en-JM", "en-NZ", "en-PH", "en-TT", "en-US", "en-ZA", "en-ZW", "eo", "es", "es-AR", 
    "es-BO", "es-CL", "es-CO", "es-CR", "es-DO", "es-EC", "es-ES", "es-GT", "es-HN", "es-MX", "es-NI", 
    "es-PA", "es-PE", "es-PR", "es-PY", "es-SV", "es-UY", "es-VE", "et", "et-EE", "eu", "eu-ES", "fa", 
    "fa-IR", "fi", "fi-FI", "fo", "fo-FO", "fr", "fr-BE", "fr-CA", "fr-CH", "fr-FR", "fr-LU", "fr-MC", 
    "gl", "gl-ES", "gu", "gu-IN", "he", "he-IL", "hi", "hi-IN", "hr", "hr-BA", "hr-HR", "hu", "hu-HU", 
    "hy", "hy-AM", "id", "id-ID", "is", "is-IS", "it", "it-CH", "it-IT", "ja", "ja-JP", "ka", "ka-GE", 
    "kk", "kk-KZ", "kn", "kn-IN", "ko", "ko-KR", "kok", "kok-IN", "ky", "ky-KG", "lt", "lt-LT", "lv", 
    "lv-LV", "mi", "mi-NZ", "mk", "mk-MK", "mn", "mn-MN", "mr", "mr-IN", "ms", "ms-BN", "ms-MY", "mt", 
    "mt-MT", "nb", "nb-NO", "nl", "nl-BE", "nl-NL", "nn-NO", "ns", "ns-ZA", "pa", "pa-IN", "pl", "pl-PL", 
    "ps", "ps-AR", "pt", "pt-BR", "pt-PT", "qu", "qu-BO", "qu-EC", "qu-PE", "ro", "ro-RO", "ru", "ru-RU", 
    "sa", "sa-IN", "se", "se-FI", "se-NO", "se-SE", "sk", "sk-SK", "sl", "sl-SI", "sq", "sq-AL", "sr-BA", 
    "sr-SP", "sv", "sv-FI", "sv-SE", "sw", "sw-KE", "syr", "syr-SY", "ta", "ta-IN", "te", "te-IN", "th", 
    "th-TH", "tl", "tl-PH", "tn", "tn-ZA", "tr", "tr-TR", "tt", "tt-RU", "ts", "uk", "uk-UA", "ur", "ur-PK", 
    "uz", "uz-UZ", "vi", "vi-VN", "xh", "xh-ZA", "zh", "zh-CN", "zh-HK", "zh-MO", "zh-SG", "zh-TW", "zu", "zu-ZA"
]

screen_res = [
    [1920, 1080], [1920, 1200], [2048, 1080], [2560, 1440], [1366, 768], 
    [1440, 900], [1536, 864], [1680, 1050], [1280, 1024], [1280, 800], 
    [1280, 720], [1600, 1200], [1600, 900],
]

def random_screen_res():
    return random.choice(screen_res)

def getFingerprint():
    fingerprint = base_fingerprint.copy()
    fingerprint["DNT"] = "unknown"
    fingerprint["L"] = random.choice(languages)
    fingerprint["D"] = random.choice([8, 24])
    fingerprint["PR"] = round(random.random() * 100) / 100 * 2 + 0.5
    fingerprint["S"] = random_screen_res()
    fingerprint["AS"] = fingerprint["S"]
    fingerprint["TO"] = (random.randint(-12, 11)) * 60
    fingerprint["SS"] = random.choice([True, False])
    fingerprint["LS"] = random.choice([True, False])
    fingerprint["IDB"] = random.choice([True, False])
    fingerprint["B"] = random.choice([True, False])
    fingerprint["ODB"] = random.choice([True, False])
    fingerprint["CPUC"] = "unknown"
    fingerprint["PK"] = "Win32"
    fingerprint["CFP"] = "canvas winding:yes~canvas fp:data:image/png;base64," + base64.b64encode(random.randbytes(128)).decode()
    fingerprint["FR"] = False
    fingerprint["FOS"] = False
    fingerprint["FB"] = False
    fingerprint["JSF"] = [jsf for jsf in fingerprint["JSF"] if random.random() > 0.5]
    fingerprint["P"] = fingerprint["P"]
    fingerprint["T"] = [0, False, False]
    fingerprint["H"] = 24
    fingerprint["SWF"] = False

    return fingerprint

# Mock of the murmur library usage
def murmur_hash_func(key, seed=0):
    return murmur_hash(key, seed)

# Equivalent to cfpHash function
def cfp_hash(H8W):
    if not H8W:
        return ""
    if hasattr(H8W, "reduce"):
        return H8W.reduce(lambda p8W, z8W: (p8W << 5) - p8W + ord(z8W) & (p8W & p8W), 0)
    l8W = 0
    if len(H8W) == 0:
        return l8W
    for k8W in H8W:
        U8W = ord(k8W)
        l8W = (l8W << 5) - l8W + U8W
        l8W = l8W & l8W
    return l8W

# Function to prepare fingerprint (equivalent to prepareF)
def prepareF(fingerprint):
    f = []
    for key, value in fingerprint.items():
        if isinstance(value, list):
            f.append(";".join(map(str, value)))
        else:
            f.append(str(value))
    return "~~~".join(f)

# Function to prepare enhanced fingerprint (equivalent to prepareFe)
def prepareFe(fingerprint):
    fe = []
    for key, value in fingerprint.items():
        if key == "CFP":
            fe.append(f"{key}:{cfp_hash(value)}")
        elif key == "P":
            fe.append(f"{key}:{[v.split('::')[0] for v in value]}")
        else:
            fe.append(f"{key}:{value}")
    return fe

# Example base fingerprint
base_enhanced_fingerprint = {
    "webgl_extensions": "ANGLE_instanced_arrays;EXT_blend_minmax;EXT_clip_control;EXT_color_buffer_half_float;EXT_depth_clamp;EXT_disjoint_timer_query;EXT_float_blend;EXT_frag_depth;EXT_polygon_offset_clamp;EXT_shader_texture_lod;EXT_texture_compression_bptc;EXT_texture_compression_rgtc;EXT_texture_filter_anisotropic;EXT_texture_mirror_clamp_to_edge;EXT_sRGB;KHR_parallel_shader_compile;OES_element_index_uint;OES_fbo_render_mipmap;OES_standard_derivatives;OES_texture_float;OES_texture_float_linear;OES_texture_half_float;OES_texture_half_float_linear;OES_vertex_array_object;WEBGL_blend_func_extended;WEBGL_color_buffer_float;WEBGL_compressed_texture_s3tc;WEBGL_compressed_texture_s3tc_srgb;WEBGL_debug_renderer_info;WEBGL_debug_shaders;WEBGL_depth_texture;WEBGL_draw_buffers;WEBGL_lose_context;WEBGL_multi_draw;WEBGL_polygon_mode",
    "webgl_extensions_hash": "7300c23f4e6fa34e534fc99c1b628588",
    "webgl_renderer": "WebKit WebGL",
    "webgl_vendor": "WebKit",
    "webgl_version": "WebGL 1.0 (OpenGL ES 2.0 Chromium)",
    "webgl_shading_language_version": "WebGL GLSL ES 1.0 (OpenGL ES GLSL ES 1.0 Chromium)",
    "webgl_aliased_line_width_range": "[1, 1]",
    "webgl_aliased_point_size_range": "[1, 1024]",
    "webgl_antialiasing": "yes",
    "webgl_bits": "8,8,24,8,8,0",
    "webgl_max_params": "16,32,16384,1024,16384,16,16384,30,16,16,4096",
    "webgl_max_viewport_dims": "[32767, 32767]",
    "webgl_unmasked_vendor": "Google Inc. (Intel)",
    "webgl_unmasked_renderer": "ANGLE (Intel, Intel(R) UHD Graphics 620 (0x00005917) Direct3D11 vs_5_0 ps_5_0, D3D11)",
    "webgl_vsf_params": "23,127,127,23,127,127,23,127,127",
    "webgl_vsi_params": "0,31,30,0,31,30,0,31,30",
    "webgl_fsf_params": "23,127,127,23,127,127,23,127,127",
    "webgl_fsi_params": "0,31,30,0,31,30,0,31,30",
    "webgl_hash_webgl": "c01cb9daa5fcef1d505c849f350dbd4a",
    "user_agent_data_brands": "Not/A)Brand,Chromium,Google Chrome",
    "user_agent_data_mobile": False,
    "navigator_connection_downlink": 10,
    "navigator_connection_downlink_max": None,
    "network_info_rtt": 50,
    "network_info_save_data": False,
    "network_info_rtt_type": None,
    "screen_pixel_depth": 24,
    "navigator_device_memory": 8,
    "navigator_pdf_viewer_enabled": True,
    "navigator_languages": "en-US",
    "window_inner_width": 0,
    "window_inner_height": 0,
    "window_outer_width": 1366,
    "window_outer_height": 728,
    "browser_detection_firefox": False,
    "browser_detection_brave": False,
    "browser_api_checks": ['permission_status: true', 'eye_dropper: true', 'audio_data: true', 'writable_stream: true', 'css_style_rule: true', 'navigator_ua: true', 'barcode_detector: false', 'display_names: true', 'contacts_manager: false', 'svg_discard_element: false', 'usb: defined', 'media_device: defined', 'playback_quality: true'],
    "browser_object_checks": "554838a8451ac36cb977e719e9d6623c",
    "29s83ih9": "68934a3e9455fa72420237eb05902327\u2063",
    "audio_codecs": "{\"ogg\":\"probably\",\"mp3\":\"probably\",\"wav\":\"probably\",\"m4a\":\"maybe\",\"aac\":\"probably\"}",
    "audio_codecs_extended": {"audio/mp4; codecs=\"mp4a.40\"":{"canPlay":"maybe","mediaSource":False},"audio/mp4; codecs=\"mp4a.40.1\"":{"canPlay":"","mediaSource":False},"audio/mp4; codecs=\"mp4a.40.2\"":{"canPlay":"probably","mediaSource":True},"audio/mp4; codecs=\"mp4a.40.5\"":{"canPlay":"probably","mediaSource":True},"audio/mp4; codecs=\"mp4a.40.29\"":{"canPlay":"probably","mediaSource":True},"audio/mp4; codecs=\"mp4a.66\"":{"canPlay":"probably","mediaSource":False},"audio/mp4; codecs=\"mp4a.67\"":{"canPlay":"probably","mediaSource":True},"audio/mp4; codecs=\"mp4a.68\"":{"canPlay":"probably","mediaSource":False},"audio/mp4; codecs=\"mp4a.69\"":{"canPlay":"probably","mediaSource":False},"audio/mp4; codecs=\"mp4a.6B\"":{"canPlay":"probably","mediaSource":False},"audio/mp4; codecs=\"mp3\"":{"canPlay":"probably","mediaSource":False},"audio/mp4; codecs=\"flac\"":{"canPlay":"probably","mediaSource":True}},
    "audio_codecs_extended_hash": None,
    "video_codecs": "{\"ogg\":\"probably\",\"h264\":\"probably\",\"webm\":\"probably\",\"mpeg4v\":\"\",\"mpeg4a\":\"\",\"theora\":\"\"}",
    "video_codecs_extended": {"video/mp4; codecs=\"hev1.1.6.L93.90\"":{"canPlay":"probably","mediaSource":True},"video/mp4; codecs=\"hvc1.1.6.L93.90\"":{"canPlay":"probably","mediaSource":True},"video/mp4; codecs=\"hev1.1.6.L93.B0\"":{"canPlay":"probably","mediaSource":True},"video/mp4; codecs=\"hvc1.1.6.L93.B0\"":{"canPlay":"probably","mediaSource":True},"video/mp4; codecs=\"vp09.00.10.08\"":{"canPlay":"probably","mediaSource":True},"video/mp4; codecs=\"vp09.00.50.08\"":{"canPlay":"probably","mediaSource":True},"video/mp4; codecs=\"vp09.01.20.08.01\"":{"canPlay":"probably","mediaSource":True},"video/mp4; codecs=\"vp09.01.20.08.01.01.01.01.00\"":{"canPlay":"probably","mediaSource":True},"video/mp4; codecs=\"vp09.02.10.10.01.09.16.09.01\"":{"canPlay":"probably","mediaSource":True},"video/mp4; codecs=\"av01.0.08M.08\"":{"canPlay":"probably","mediaSource":True},"video/webm; codecs=\"vorbis\"":{"canPlay":"probably","mediaSource":True},"video/webm; codecs=\"vp8\"":{"canPlay":"probably","mediaSource":True},"video/webm; codecs=\"vp8.0\"":{"canPlay":"probably","mediaSource":False},"video/webm; codecs=\"vp8.0, vorbis\"":{"canPlay":"probably","mediaSource":False},"video/webm; codecs=\"vp8, opus\"":{"canPlay":"probably","mediaSource":True},"video/webm; codecs=\"vp9\"":{"canPlay":"probably","mediaSource":True},"video/webm; codecs=\"vp9, vorbis\"":{"canPlay":"probably","mediaSource":True},"video/webm; codecs=\"vp9, opus\"":{"canPlay":"probably","mediaSource":True},"video/x-matroska; codecs=\"theora\"":{"canPlay":"","mediaSource":False},"application/x-mpegURL; codecs=\"avc1.42E01E\"":{"canPlay":"","mediaSource":False},"video/ogg; codecs=\"dirac, vorbis\"":{"canPlay":"","mediaSource":False},"video/ogg; codecs=\"theora, speex\"":{"canPlay":"","mediaSource":False},"video/ogg; codecs=\"theora, vorbis\"":{"canPlay":"","mediaSource":False},"video/ogg; codecs=\"theora, flac\"":{"canPlay":"","mediaSource":False},"video/ogg; codecs=\"dirac, flac\"":{"canPlay":"","mediaSource":False},"video/ogg; codecs=\"flac\"":{"canPlay":"probably","mediaSource":False},"video/3gpp; codecs=\"mp4v.20.8, samr\"":{"canPlay":"","mediaSource":False}},
    "video_codecs_extended_hash": None,
    "media_query_dark_mode": True,
    "css_media_queries": 0,
    "css_color_gamut": 'srgb',
    "css_contrast": 'no-preference',
    "css_monochrome": False,
    "css_pointer": 'fine',
    "css_grid_support": False,
    "headless_browser_phantom": False,
    "headless_browser_selenium": False,
    "headless_browser_nightmare_js": False,
    "headless_browser_generic": 4,
    "1l2l5234ar2": "1721443601093\u2062",
    "document__referrer": "https://www.roblox.com/",
    "window__ancestor_origins": [
        "https://www.roblox.com",
    ],
    "window__tree_index": [1, 0],
    "window__tree_structure": "[[],[[]]]",
    "window__location_href": "",
    "client_config__sitedata_location_href": "",
    "client_config__surl": "",
    "client_config__language": None,
    "c8480e29a": None,
    "client_config__triggered_inline": False,
    "mobile_sdk__is_sdk": False,
    "audio_fingerprint": "124.04347527516074",
    "navigator_battery_charging": True,
    "media_device_kinds": ['audioinput', 'videoinput', 'audiooutput'],
    "media_devices_hash": None,
    "navigator_permissions_hash": "67419471976a14a1430378465782c62d",
    "math_fingerprint": "3b2ff195f341257a6a2abbc122f4ae67",
    "supported_math_functions": "e9dd4fafb44ee489f48f7c93d0f48163",
    "screen_orientation": "landscape-primary",
    "rtc_peer_connection": 5,
    "4b4b269e68": None,
    "6a62b2a558": None,
    "speech_default_voice": "Microsoft David - English (United States) || en-US",
    "speech_voices_hash": None
}

# Function to generate the enhanced fingerprint
def getEnhancedFingerprint(site = None, surl = None):
    md5 = hashlib.md5()
    md5.update(surl.encode('utf-8'))
    surlhash = md5.hexdigest()
    fingerprint = base_enhanced_fingerprint
    fingerprint["audio_codecs_extended_hash"] = "805036349642e2569ec299baed02315b"
    fingerprint["video_codecs_extended_hash"] = "67b509547efe3423d32a3a70a2553c16"
    fingerprint["4b4b269e68"] = str(uuid.uuid4())
    fingerprint["6a62b2a558"] = "5a2a74a1ccf39f6b2719561c6aad2dcc"
    fingerprint["speech_voices_hash"] = "b24bd471a2b801a80c0e3592b0c0c362"
    fingerprint["media_devices_hash"] = "199eba60310b53c200cc783906883c67"
    fingerprint["c8480e29a"] = surlhash
    if site is not None:
        fingerprint["window__ancestor_origins"] = [site, site]
        fingerprint["client_config__sitedata_location_href"] = site
        fingerprint["client_config__surl"] = surl
        fingerprint["window__location_href"] = f"{surl}/v2/2.8.2/enforcement.5a2a74a1ccf39f6b2719561c6aad2dcc.html"
        fingerprint["document__referrer"] = site
    fingerprint["audio_fingerprint"] = str(124.04347527516074 + random.uniform(-0.0005, 0.0005))
    
    enhanced_fingerprint_list = [
        {"key": key, "value": value}
        for key, value in fingerprint.items()
    ]
    
    return enhanced_fingerprint_list