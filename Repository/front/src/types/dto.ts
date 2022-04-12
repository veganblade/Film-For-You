export interface AuthDTO {
    login: string;
    password: string;
    code?: string | undefined;
    message?: string | undefined;
    isAdmin?: string;
}

export interface SignOutDTO {
    code: number;
    message: string;
}

export interface SendRequestsToBuyDto {
  status: number;
  message: string;
}