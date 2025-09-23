import type {
	HelloWorldResponse,
	HealthApiResponse,
	DiagnoseRequest,
	SmokingCounselingResponse,
	HealthStatusResponse,
	AnalyzeImageResponse,
	GenerateImageResponse,
} from "../interface";

// Cloud Run APIのベースURL
const CLOUD_RUN_API_BASE_URL =
	"https://no-smoking-api-9987299071.asia-northeast1.run.app";

const SESSION_ID = crypto.randomUUID();

/**
 * 共通のAPI fetch関数（ジェネリック型付き）
 * @template T - レスポンスデータの型
 * @param endpoint - APIエンドポイント
 * @param options - fetchオプション
 * @returns Promise<T> - APIレスポンス
 * @throws ApiError - APIエラー時
 */
async function apiFetch<T>(
	endpoint: string,
	options: RequestInit = {}
): Promise<T> {
	try {
		const url = `${CLOUD_RUN_API_BASE_URL}${endpoint}`;

		// デフォルトオプション
		const defaultOptions: RequestInit = {
			mode: "cors",
			headers: {
				...(!(options.body instanceof FormData) && {
					"Content-Type": "application/json",
				}),
			},
		};

		// オプションをマージ
		const mergedOptions: RequestInit = {
			...defaultOptions,
			...options,
			headers: {
				...defaultOptions.headers,
				...options.headers,
			},
		};

		const response = await fetch(url, mergedOptions);

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
 * Cloud Run APIからHello Worldメッセージを取得する関数
 * @returns Promise<HelloWorldResponse> - Hello Worldメッセージ
 * @throws ApiError - APIエラー時
 */
export async function fetchHelloWorld(): Promise<HelloWorldResponse> {
	return apiFetch<HelloWorldResponse>("/hello", {
		method: "GET",
	});
}

/**
 * ヘルスステータスを取得する関数
 * @returns Promise<HealthStatusResponse> - ヘルスステータス
 * @throws ApiError - APIエラー時
 */
export async function fetchHealthStatus(): Promise<HealthStatusResponse> {
	return apiFetch<HealthStatusResponse>("/health/status", {
		method: "GET",
	});
}

/**
 * 画像を解析する関数
 * @param formData - マルチパートフォームデータ（画像ファイルを含む）
 * @returns Promise<AnalyzeImageResponse> - 画像解析結果
 * @throws ApiError - APIエラー時
 */
/**
 * curl -i -X POST \
   -H "Content-Type:multipart/form-data" \
   -F "file=@\"./Generated Image September 20, 2025 - 11_11AM.png\";type=image/png;filename=\"Generated Image September 20, 2025 - 11_11AM.png\"" \
 'https://no-smoking-api-9987299071.asia-northeast1.run.app/api/analyze-image'
*/
//上記の使用例のように、formDataに画像ファイルを含むマルチパートフォームデータを渡す
export async function fetchAnalyzeImage(
	formData: FormData
): Promise<AnalyzeImageResponse> {
	return apiFetch<AnalyzeImageResponse>("/api/analyze-image", {
		method: "POST",
		body: formData,
	});
}

/**
 * 画像を生成する関数
 * @param formData - マルチパートフォームデータ（プロンプトやパラメータを含む）
 * @returns Promise<GenerateImageResponse> - 画像生成結果
 * @throws ApiError - APIエラー時
 */
export async function fetchGenerateImage(
	formData: FormData
): Promise<GenerateImageResponse> {
	return apiFetch<GenerateImageResponse>("/api/generate-image", {
		method: "POST",
		body: formData,
	});
}

/**
 * APIの全体的なヘルス状況を取得する関数
 * @returns Promise<HealthApiResponse> - APIヘルス情報
 * @throws ApiError - APIエラー時
 */
export async function fetchApiHealth(): Promise<HealthApiResponse> {
	return apiFetch<HealthApiResponse>("/health", {
		method: "GET",
	});
}

/**
 * 喫煙カウンセリングを実行する関数
 * @param formData - 喫煙カウンセリング用のフォームデータ
 * @returns Promise<SmokingCounselingResponse> - カウンセリング結果
 * @throws ApiError - APIエラー時
 */
export async function fetchSmokingCounseling(
	formData: DiagnoseRequest
): Promise<SmokingCounselingResponse> {
	const payload = {
		session_id: SESSION_ID,
		questionnaire: formData,
	};
	return apiFetch<SmokingCounselingResponse>("/api/diagnose", {
		method: "POST",
		body: JSON.stringify(payload),
	});
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
