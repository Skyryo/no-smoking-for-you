/**
 * APIレスポンスの型定義
 */
export interface HelloWorldResponse {
	message: string;
}

/**
 * ヘルスステータスレスポンスの型定義
 */
export interface HealthStatusResponse {
	status: string;
	timestamp: string;
	version?: string;
}

/**
 * 診断リクエストの型定義
 */
export interface DiagnoseRequest {
	current_age: number;
	gender: Gender;
	smoking_start_age: number;
	daily_cigarettes: number;
	cigarette_type: CigaretteType;
	cigarette_brand?: string;
	quit_attempts: number;
	current_health_issues?: string[];
	exercise_frequency: number;
	alcohol_consumption: number;
	sleep_hours: number;
	previous_medical_advice?: string;
}

/**
 * 診断レスポンスの型定義
 */
export interface DiagnoseResponse {
	diagnosis: string;
	confidence: number;
	recommendations: string[];
	riskLevel: "low" | "medium" | "high";
	timestamp: string;
}

/**
 * 画像解析レスポンスの型定義
 */
export interface AnalyzeImageResponse {
	analysis: string;
	detectedObjects: string[];
	confidence: number;
	metadata: {
		imageSize: string;
		format: string;
		timestamp: string;
	};
}

/**
 * 画像生成レスポンスの型定義
 */
export interface GenerateImageResponse {
	image_base64: string;
	success: boolean;
}

/**
 * ヘルスAPIレスポンスの型定義
 */
export interface HealthApiResponse {
	status: "healthy" | "degraded" | "unhealthy";
	uptime: number;
	timestamp: string;
	services: {
		database: "up" | "down";
		storage: "up" | "down";
		ai: "up" | "down";
	};
}

/**
 * 性別の列挙型
 */
export type Gender = "male" | "female" | "other";

/**
 * タバコの種類の列挙型
 */
export type CigaretteType = "通常タバコ" | "メンソールタバコ" | "電子タバコ";

/**
 * 喫煙カウンセリング結果の型定義
 */
export interface SmokingCounselingResponse {
	counseling_result: string;
	recommendations: string[];
	risk_assessment: {
		level: "low" | "medium" | "high" | "very_high";
		factors: string[];
	};
	personalized_plan: {
		short_term_goals: string[];
		long_term_goals: string[];
		support_resources: string[];
	};
	timestamp: string;
}
