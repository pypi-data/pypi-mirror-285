const NodeRSA = require('node-rsa');
const crypto = require('crypto');
const CryptoJS = require("crypto-js");

const https = require('https');
// process.env.DEFAULT_ENCODING = 'utf8';
// console.log('Node.js Version:', process.version);
// console.log('Node.js Environment:', process.env.NODE_ENV);
// console.log('Default Encoding:', process.env.DEFAULT_ENCODING);

function get_key() {
    var s4 = "";
    for (i = 0; i < 4; i++) {
        s4 = s4 + ((1 + Math["random"]()) * 65536 | 0)["toString"](16)["substring"](1);
    }
    return s4;
}

function MD5_Encrypt(word) {
    return CryptoJS.MD5(word).toString();
}

function AES_Encrypt(key, word) {
    var srcs = CryptoJS.enc.Utf8.parse(word);
    var encrypted = CryptoJS.AES.encrypt(srcs, CryptoJS.enc.Utf8.parse(key), {
        iv: CryptoJS.enc.Utf8.parse("0000000000000000"),
        mode: CryptoJS.mode.CBC,
        padding: CryptoJS.pad.Pkcs7
    });
    return CryptoJS.enc.Hex.stringify(CryptoJS.enc.Base64.parse(encrypted.toString()));
}

function RSA_encrypt(data) {
    const public_key_1 = '00C1E3934D1614465B33053E7F48EE4EC87B14B95EF88947713D25EECBFF7E74C7977D02DC1D9451F79DD5D1C10C29ACB6A9B4D6FB7D0A0279B6719E1772565F09AF627715919221AEF91899CAE08C0D686D748B20A3603BE2318CA6BC2B59706592A9219D0BF05C9F65023A21D2330807252AE0066D59CEEFA5F2748EA80BAB81';
    const public_key_2 = '10001';
    const public_key = new NodeRSA();
    public_key.importKey({
        n: Buffer.from(public_key_1, 'hex'),
        e: parseInt(public_key_2, 16),
    }, 'components-public');
    const encrypted = crypto.publicEncrypt({
        key: public_key.exportKey('public'),
        padding: crypto.constants.RSA_PKCS1_PADDING
    }, Buffer.from(data));
    return encrypted.toString('hex');
}

function get_w(captchaId, lot_number, detail_time, distance, daily_str) {
    romdon_key = get_key()
    pow_msg = "1|0|md5|" + detail_time + "|" + captchaId + "|" + lot_number + "||" + romdon_key
    xiyu = {
        "device_id": "",
        "lot_number": lot_number,
        "pow_msg": pow_msg,
        "pow_sign": MD5_Encrypt(pow_msg),
        "geetest": "captcha",
        "lang": "zh",
        "ep": "123",
        "biht": "1426265548",
        "em": {"ph": 0, "cp": 0, "ek": "11", "wd": 1, "nt": 0, "si": 0, "sc": 0},
        "oVxD":"EwR5"
        // "Wf3q":"TI7T"
        // "Sqk5":"qXYv"
        // "Dqf2":"zgWV"
        // "Dqf2":"zgWV",
        // "dyG3":"jGU8",
        // "MRwL":"3vDL",
        // "lWq7":"uoW6"
        // "rGcd":"pgzq"
        // "rHHD":"9OTz"
        // "rifd":"stRA"
        // "x1HJ":"8FFD"
        // "ujM6":"9RhE"
    }
    xiyu = JSON.stringify(xiyu).replace(" ", "").replace("'", '"')
    w = AES_Encrypt(romdon_key, xiyu) + RSA_encrypt(romdon_key)
    return w
}

// const axios = require('axios');
// const { v4: uuidv4 } = require('uuid');
// async function load_js_handle(captchaId) {
//     const challenge = uuidv4();
//     const fileUrl = `https://gcaptcha4.geetest.com/load?captcha_id=${captchaId}&challenge=${challenge}&client_type=web&lang=zh-cn&callback=geetest_${Date.now().toString()}`;
//     try {
//         const data = (await axios.get(fileUrl)).data;
//         const result = data.substring(data.indexOf('(') + 1, data.lastIndexOf(')'));
//         const jsonData = JSON.parse(result).data;
//         // console.log('JSON 响应参数:', jsonData);
//         const js_url = 'https://static.geetest.com' + jsonData.static_path + jsonData.js
//         console.log('js url:', js_url);
//         const js_data = (await axios.get(js_url)).data;
//         const startIndex = js_data.indexOf("decodeURI(") + 11;
//         const endIndex = js_data.lastIndexOf("3');");
//         return js_data.substring(startIndex, endIndex + 1)
//     } catch (error) {
//         console.error('发生错误：', error);
//     }
// }
//
//
// const lclRz = (async (captchaId) => {
//     const encodedKey = '8)amnz';
//     let dataToDecode = await load_js_handle(captchaId);
//     dataToDecode = `${dataToDecode}`.replaceAll('\'', '')
//     // const dataToDecode =
//     console.log(dataToDecode.length);
//     const decodedData = decodeData(dataToDecode, encodedKey);
//     console.log(decodedData.length);
//
//     function decodeData(data, encodedKey) {
//         const decodedData = decodeURIComponent(data);
//         const keyLength = encodedKey.length;
//         let decodedResult = '';
//
//         for (let i = 0; i < decodedData.length; i++) {
//             const keyChar = encodedKey.charCodeAt(i % keyLength);
//             decodedResult += String.fromCharCode(decodedData.charCodeAt(i) ^ keyChar);
//         }
//         return decodedResult.split('^');
//     }
//     return {
//         decode: (index) => decodedData[index]
//     };
// })
//
// async function get_daily_str(captchaId) {
//     try {
//         const result = await lclRz(captchaId);
//         const decodedValue = result.decode([773]); // 传递要获取的索引
//         console.log('解码后的值:', decodedValue);
//         return decodedValue;
//     } catch (error) {
//         console.error('发生错误：', error);
//         return null; // 或者返回适当的错误值
//     }
// }
// get_daily_str("244bcb8b9846215df5af4c624a750db4").then((value) => {
//     console.log(value);
// })