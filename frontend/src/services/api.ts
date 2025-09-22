// Cloud Run APIのベースURL
const CLOUD_RUN_API_BASE_URL =
	"https://no-smoking-api-9987299071.asia-northeast1.run.app";

/**
 * APIレスポンスの型定義
 */
export interface HelloWorldResponse {
	message: string;
}

/**
 * APIエラーの型定義
 */
interface ApiErrorInterface {
	message: string;
	status?: number;
}

/**
 * Cloud Run APIからHello Worldメッセージを取得する関数
 * @returns Promise<HelloWorldResponse> - Hello Worldメッセージ
 * @throws ApiError - APIエラー時
 */
export async function fetchHelloWorld(): Promise<HelloWorldResponse> {
	try {
		const response = await fetch(`${CLOUD_RUN_API_BASE_URL}/hello`, {
			method: "GET",
			headers: {
				"Content-Type": "application/json",
			},
			// CORS対応
			mode: "cors",
		});

		if (!response.ok) {
			throw new ApiError({
				message: `HTTP error! status: ${response.status}`,
				status: response.status,
			});
		}

		const data = await response.json();
		return data;
	} catch (error) {
		if (error instanceof ApiError) {
			throw error;
		}

		// ネットワークエラーやその他のエラー
		throw new ApiError({
			message:
				error instanceof Error ? error.message : "Unknown error occurred",
		});
	}
}

/**
 * エラークラス
 */
export class ApiError extends Error {
	status?: number;

	constructor({ message, status }: { message: string; status?: number }) {
		super(message);
		this.name = "ApiError";
		this.status = status;
	}
}
