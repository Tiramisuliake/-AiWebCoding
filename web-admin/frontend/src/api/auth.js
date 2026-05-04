import http from "./http";

export async function login(payload) {
  const { data } = await http.post("/auth/login", payload);
  return data;
}

export async function logout(refreshTokenValue) {
  const { data } = await http.post("/auth/logout", {
    refresh_token: refreshTokenValue
  });
  return data;
}

export async function refreshToken(refreshTokenValue) {
  const { data } = await http.post(
    "/auth/refresh",
    {},
    {
      headers: {
        Authorization: `Bearer ${refreshTokenValue}`
      }
    }
  );
  return data;
}
