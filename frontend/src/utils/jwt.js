// 簡易 JWT 簽章模擬（請在實際應用中改用後端簽章）
export function generateJWT(userSn, expTs) {
  const header = {
    alg: "HS256",
    typ: "JWT"
  };

  const payload = {
    userSn: userSn,
    exp: expTs
  };

  function base64urlEncode(obj) {
    return btoa(JSON.stringify(obj))
      .replace(/=/g, '')
      .replace(/\+/g, '-')
      .replace(/\//g, '_');
  }

  const encodedHeader = base64urlEncode(header);
  const encodedPayload = base64urlEncode(payload);

  // 簽章模擬
  const fakeSignature = btoa('signature').replace(/=/g, '');
  return `${encodedHeader}.${encodedPayload}.${fakeSignature}`;
}