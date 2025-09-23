import React, { useState } from "react";
import {
	Box,
	Card,
	CardContent,
	CardHeader,
	TextField,
	FormControl,
	FormControlLabel,
	FormLabel,
	RadioGroup,
	Radio,
	Select,
	MenuItem,
	InputLabel,
	Chip,
	OutlinedInput,
	Button,
	Typography,
	Divider,
	Alert,
	CircularProgress,
	Slider,
	Stack,
} from "@mui/material";
import {
	SmokingRoomsOutlined as SmokingIcon,
	HealthAndSafetyOutlined as HealthIcon,
	PersonOutlined as PersonIcon,
} from "@mui/icons-material";
import {
	fetchSmokingCounseling,
	fetchAnalyzeImage,
	fetchGenerateImage,
	ApiError,
} from "../services/api";
import type {
	DiagnoseRequest,
	Gender,
	CigaretteType,
	SmokingCounselingResponse,
} from "../interface";
import ImageUploader from "./ImageUploader";

// 健康問題の選択肢
const HEALTH_ISSUES_OPTIONS = [
	"呼吸器系の問題",
	"心血管系の問題",
	"高血圧",
	"糖尿病",
	"肥満",
	"睡眠障害",
	"ストレス・不安",
	"その他",
];

function QuestionnaireForm() {
	// フォームデータの状態管理
	const [formData, setFormData] = useState<DiagnoseRequest>({
		current_age: 30,
		gender: "male" as Gender,
		smoking_start_age: 20,
		daily_cigarettes: 10,
		cigarette_type: "通常タバコ",
		cigarette_brand: "",
		quit_attempts: 0,
		current_health_issues: [],
		exercise_frequency: 0,
		alcohol_consumption: 0,
		sleep_hours: 7.0,
		previous_medical_advice: "",
	});
	const [file, setFile] = useState<File | null>(null);

	// UI状態の管理
	const [loading, setLoading] = useState(false);
	const [result, setResult] = useState<SmokingCounselingResponse | null>(null);
	const [error, setError] = useState<string | null>(null);
	const [base64Image, setBase64Image] = useState<string | null>(null);

	// フォームデータの更新関数
	const updateFormData = (field: keyof DiagnoseRequest, value: any) => {
		setFormData((prev) => ({
			...prev,
			[field]: value,
		}));
	};

	// 健康問題の選択変更
	const handleHealthIssuesChange = (event: any) => {
		const value = event.target.value;
		updateFormData(
			"current_health_issues",
			typeof value === "string" ? value.split(",") : value
		);
	};

	// フォーム送信処理
	const handleSubmit = async (event: React.FormEvent) => {
		event.preventDefault();
		setLoading(true);
		setError(null);
		if (!file) {
			setError("画像ファイルをアップロードしてください");
			setLoading(false);
			return;
		}
		try {
			// 画像解析用のFormDataを作成
			const imageFormData = new FormData();
			imageFormData.append("file", file);

			// カウンセリングと画像解析を並列実行
			const [response, responseAnalyzeImage] = await Promise.all([
				fetchSmokingCounseling(formData),
				fetchAnalyzeImage(imageFormData),
			]);

			// 画像生成用のFormDataを作成
			const generateFormData = new FormData();
			generateFormData.append("file", file);
			// generateFormData.append(
			// 	"prompt",
			// 	`カウンセリング結果：${JSON.stringify(
			// 		response
			// 	)}、画像解析結果：${JSON.stringify(responseAnalyzeImage)}`
			// );
			generateFormData.append(
				"prompt",
				"20年後の喫煙による健康被害をリアルに描写した画像を生成して"
			);
			const responseGenerateImage = await fetchGenerateImage(generateFormData);
			console.log("Generated Image response:", responseGenerateImage);
			console.log("Counseling response:", response);
			setBase64Image(responseGenerateImage.image_base64);
			setResult(response);
		} catch (err) {
			if (err instanceof ApiError) {
				setError(`APIエラー: ${err.message}`);
			} else {
				setError("予期しないエラーが発生しました");
			}
		} finally {
			setLoading(false);
		}
	};

	// 結果表示
	if (result) {
		return (
			<Card sx={{ maxWidth: 800, margin: "20px auto" }}>
				<CardHeader
					title="喫煙カウンセリング結果"
					avatar={<HealthIcon color="primary" />}
				/>
				<CardContent>
					<Typography variant="h6" gutterBottom>
						カウンセリング結果
					</Typography>
					<Typography paragraph>{result.counseling_result}</Typography>
					{base64Image && (
						<Box textAlign="center" my={2}>
							<img
								src={`data:image/png;base64,${base64Image}`}
								alt="Generated Result"
								style={{ maxWidth: "100%", height: "auto", borderRadius: 8 }}
							/>
						</Box>
					)}

					<Divider sx={{ my: 2 }} />

					<Typography variant="h6" gutterBottom>
						推奨事項
					</Typography>
					{/* {result.recommendations.map((recommendation, index) => (
						<Typography key={index} paragraph>
							• {recommendation}
						</Typography>
					))} */}

					<Divider sx={{ my: 2 }} />

					<Button
						variant="outlined"
						onClick={() => setResult(null)}
						sx={{ mt: 2 }}
					>
						新しく診断する
					</Button>
				</CardContent>
			</Card>
		);
	}

	return (
		<Box sx={{ maxWidth: 800, margin: "20px auto", padding: 2 }}>
			<Card>
				<CardHeader
					title="喫煙状況カウンセリング"
					subheader="あなたの喫煙状況について詳しくお聞かせください"
					avatar={<SmokingIcon color="primary" />}
				/>
				<CardContent>
					<form onSubmit={handleSubmit}>
						{/* 基本情報セクション */}
						<Box sx={{ mb: 4 }}>
							<Typography
								variant="h6"
								sx={{ mb: 2, display: "flex", alignItems: "center", gap: 1 }}
							>
								<PersonIcon /> 基本情報
							</Typography>

							<Box
								sx={{
									display: "flex",
									flexDirection: { xs: "column", sm: "row" },
									gap: 2,
									mb: 2,
								}}
							>
								<TextField
									fullWidth
									label="現在の年齢"
									type="number"
									value={formData.current_age}
									onChange={(e) =>
										updateFormData("current_age", parseInt(e.target.value))
									}
									inputProps={{ min: 1, max: 120 }}
									required
								/>

								<FormControl fullWidth required>
									<FormLabel>性別</FormLabel>
									<RadioGroup
										row
										value={formData.gender}
										onChange={(e) =>
											updateFormData("gender", e.target.value as Gender)
										}
									>
										<FormControlLabel
											value="male"
											control={<Radio />}
											label="男性"
										/>
										<FormControlLabel
											value="female"
											control={<Radio />}
											label="女性"
										/>
										<FormControlLabel
											value="other"
											control={<Radio />}
											label="その他"
										/>
									</RadioGroup>
								</FormControl>
							</Box>
						</Box>

						<Divider sx={{ my: 3 }} />

						{/* 喫煙情報セクション */}
						<Box sx={{ mb: 4 }}>
							<Typography
								variant="h6"
								sx={{ mb: 2, display: "flex", alignItems: "center", gap: 1 }}
							>
								<SmokingIcon /> 喫煙情報
							</Typography>

							<Stack spacing={2}>
								<Box
									sx={{
										display: "flex",
										flexDirection: { xs: "column", sm: "row" },
										gap: 2,
									}}
								>
									<TextField
										fullWidth
										label="喫煙開始年齢"
										type="number"
										value={formData.smoking_start_age}
										onChange={(e) =>
											updateFormData(
												"smoking_start_age",
												parseInt(e.target.value)
											)
										}
										inputProps={{ min: 1, max: 120 }}
										required
									/>

									<TextField
										fullWidth
										label="1日あたり喫煙本数"
										type="number"
										value={formData.daily_cigarettes}
										onChange={(e) =>
											updateFormData(
												"daily_cigarettes",
												parseInt(e.target.value)
											)
										}
										inputProps={{ min: 0, max: 100 }}
										required
									/>
								</Box>

								<Box
									sx={{
										display: "flex",
										flexDirection: { xs: "column", sm: "row" },
										gap: 2,
									}}
								>
									<FormControl fullWidth required>
										<InputLabel>タバコの種類</InputLabel>
										<Select
											value={formData.cigarette_type}
											label="タバコの種類"
											onChange={(e) =>
												updateFormData(
													"cigarette_type",
													e.target.value as CigaretteType
												)
											}
										>
											<MenuItem value="通常タバコ">通常のタバコ</MenuItem>
											<MenuItem value="メンソールタバコ">
												メンソールタバコ
											</MenuItem>
											<MenuItem value="電子タバコ">電子タバコ</MenuItem>
										</Select>
									</FormControl>

									<TextField
										fullWidth
										label="ブランド名（任意）"
										value={formData.cigarette_brand}
										onChange={(e) =>
											updateFormData("cigarette_brand", e.target.value)
										}
										inputProps={{ maxLength: 32 }}
									/>
								</Box>

								<TextField
									fullWidth
									label="禁煙試行回数"
									type="number"
									value={formData.quit_attempts}
									onChange={(e) =>
										updateFormData("quit_attempts", parseInt(e.target.value))
									}
									inputProps={{ min: 0, max: 99 }}
									required
								/>
							</Stack>
						</Box>

						<Divider sx={{ my: 3 }} />

						{/* 健康・ライフスタイル情報セクション */}
						<Box sx={{ mb: 4 }}>
							<Typography
								variant="h6"
								sx={{ mb: 2, display: "flex", alignItems: "center", gap: 1 }}
							>
								<HealthIcon /> 健康・ライフスタイル情報
							</Typography>

							<Stack spacing={3}>
								<FormControl fullWidth>
									<InputLabel>現在の健康問題（任意・複数選択可）</InputLabel>
									<Select
										multiple
										value={formData.current_health_issues || []}
										onChange={handleHealthIssuesChange}
										input={
											<OutlinedInput label="現在の健康問題（任意・複数選択可）" />
										}
										renderValue={(selected) => (
											<Box sx={{ display: "flex", flexWrap: "wrap", gap: 0.5 }}>
												{selected.map((value) => (
													<Chip key={value} label={value} size="small" />
												))}
											</Box>
										)}
									>
										{HEALTH_ISSUES_OPTIONS.map((option) => (
											<MenuItem key={option} value={option}>
												{option}
											</MenuItem>
										))}
									</Select>
								</FormControl>

								<Box
									sx={{
										display: "flex",
										flexDirection: { xs: "column", sm: "row" },
										gap: 4,
									}}
								>
									<Box sx={{ flexGrow: 1 }}>
										<Typography gutterBottom>
											運動頻度（週{formData.exercise_frequency}回）
										</Typography>
										<Slider
											value={formData.exercise_frequency}
											onChange={(_, value) =>
												updateFormData("exercise_frequency", value as number)
											}
											min={0}
											max={7}
											marks
											step={1}
											valueLabelDisplay="auto"
										/>
									</Box>

									<Box sx={{ flexGrow: 1 }}>
										<Typography gutterBottom>
											飲酒頻度（週{formData.alcohol_consumption}回）
										</Typography>
										<Slider
											value={formData.alcohol_consumption}
											onChange={(_, value) =>
												updateFormData("alcohol_consumption", value as number)
											}
											min={0}
											max={7}
											marks
											step={1}
											valueLabelDisplay="auto"
										/>
									</Box>
								</Box>

								<TextField
									fullWidth
									label="睡眠時間"
									type="number"
									value={formData.sleep_hours}
									onChange={(e) =>
										updateFormData("sleep_hours", parseFloat(e.target.value))
									}
									inputProps={{ min: 0, max: 24, step: 0.5 }}
									helperText="時間単位で入力してください"
									required
									sx={{ maxWidth: "50%" }}
								/>

								<TextField
									fullWidth
									label="過去の医師からの助言（任意）"
									multiline
									rows={3}
									value={formData.previous_medical_advice}
									onChange={(e) =>
										updateFormData("previous_medical_advice", e.target.value)
									}
									inputProps={{ maxLength: 128 }}
								/>
							</Stack>
						</Box>

						{/* エラー表示 */}
						{error && (
							<Alert severity="error" sx={{ mb: 3 }}>
								{error}
							</Alert>
						)}

						<ImageUploader setFile={setFile} />
						{/* 送信ボタン */}
						<Box sx={{ display: "flex", justifyContent: "center", mt: 4 }}>
							<Button
								type="submit"
								variant="contained"
								size="large"
								disabled={loading}
								startIcon={
									loading ? <CircularProgress size={20} /> : <HealthIcon />
								}
								sx={{ minWidth: 200 }}
							>
								{loading ? "カウンセリング中..." : "カウンセリング開始"}
							</Button>
						</Box>
					</form>
				</CardContent>
			</Card>
		</Box>
	);
}

export default QuestionnaireForm;
