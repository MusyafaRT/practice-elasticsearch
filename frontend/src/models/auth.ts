export interface UserLoginData {
  user_data: UserLoginDatum | undefined | null;
  access_token: string;
  refresh_token: string;
}

export interface UserLoginDatum {
  id: string;
  first_name: string;
  last_name: string;
  email: string;
  oauth_provider: null;
  profile_picture: null;
  is_oauth_user: boolean;
}

export interface UserDataDatum {
  id: string;
  first_name: string;
  last_name: string;
  email: string;
  oauth_provider: null;
  profile_picture: null;
  is_oauth_user: boolean;
}

export interface ReqUserLogin {
  email: string;
  password: string;
}

export interface ReqUserRegister {
  first_name: string;
  last_name: string;
  email: string;
  password: string;
}

export interface GoogleOAuthLogin {
  authorization_url: string;
  state: string;
}

export interface ReqOAuth {
  provider: string;
}

export interface ResUserToken {
  access_token: string;
  refresh_token: string;
}
