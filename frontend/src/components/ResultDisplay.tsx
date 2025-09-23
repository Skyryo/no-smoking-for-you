import {
	Card,
	CardHeader,
	CardContent,
	Typography,
	Divider,
	Button,
	Box,
	Paper,
	Chip,
} from "@mui/material";
import HealthIcon from "@mui/icons-material/HealthAndSafety";
import LightModeIcon from "@mui/icons-material/LightMode";
import DarkModeIcon from "@mui/icons-material/DarkMode";
import type { SmokingCounselingResponse } from "../interface";

interface ResultDisplayProps {
	currentImage: string;
	futureImage: string;
	diagnosisReport: SmokingCounselingResponse;
	imageAnalysisResult: string;
	onClickReset: () => void;
}

function ResultDisplay(props: ResultDisplayProps) {
	const {
		currentImage,
		futureImage,
		diagnosisReport,
		imageAnalysisResult,
		onClickReset,
	} = props;

	return (
		<Card
			sx={{
				maxWidth: 800,
				margin: "20px auto",
				borderRadius: 3,
				boxShadow: 3,
			}}
		>
			<CardHeader
				title="喫煙カウンセリング結果"
				avatar={<HealthIcon color="primary" />}
				sx={{
					background: "linear-gradient(45deg, #FF6B6B 30%, #4ECDC4 90%)",
					color: "white",
					"& .MuiCardHeader-avatar": {
						backgroundColor: "rgba(255,255,255,0.2)",
						borderRadius: "50%",
						padding: "8px",
					},
				}}
			/>
			<CardContent sx={{ p: 3 }}>
				{/* 画像比較セクション */}
				<Box sx={{ mb: 4 }}>
					<Typography
						variant="h5"
						gutterBottom
						textAlign="center"
						sx={{
							fontWeight: "bold",
							color: "#333",
							mb: 3,
						}}
					>
						あなたの未来を見てみましょう
					</Typography>

					<Box
						sx={{
							display: "flex",
							flexDirection: { xs: "column", md: "row" },
							gap: 3,
							width: "100%",
						}}
					>
						{/* 現在の画像 */}
						<Box sx={{ flex: 1 }}>
							<Paper
								elevation={4}
								sx={{
									p: 2,
									borderRadius: 3,
									background:
										"linear-gradient(135deg, #FFE082 0%, #FFF59D 50%, #FFECB3 100%)",
									border: "3px solid #FFC107",
									position: "relative",
									overflow: "hidden",
									"&::before": {
										content: '""',
										position: "absolute",
										top: 0,
										left: 0,
										right: 0,
										bottom: 0,
										background:
											"radial-gradient(circle at top right, rgba(255,255,255,0.4) 0%, transparent 50%)",
										pointerEvents: "none",
									},
								}}
							>
								<Box sx={{ textAlign: "center", mb: 2 }}>
									<Chip
										icon={<LightModeIcon />}
										label="現在のあなた"
										sx={{
											backgroundColor: "#FF9800",
											color: "white",
											fontWeight: "bold",
											fontSize: "1rem",
											px: 2,
										}}
									/>
								</Box>
								{currentImage && (
									<Box
										sx={{
											textAlign: "center",
											position: "relative",
										}}
									>
										<img
											src={`data:image/png;base64,${currentImage}`}
											alt="現在のあなた"
											style={{
												maxWidth: "85%",
												height: "auto",
												borderRadius: 12,
												boxShadow: "0 4px 8px rgba(0,0,0,0.1)",
											}}
										/>
									</Box>
								)}
								<Typography
									variant="body2"
									textAlign="center"
									sx={{
										mt: 2,
										color: "#E65100",
										fontWeight: "medium",
									}}
								>
									健康的で輝いているあなた ✨
								</Typography>
							</Paper>
						</Box>

						{/* 未来の画像 */}
						<Box sx={{ flex: 1 }}>
							<Paper
								elevation={6}
								sx={{
									p: 2,
									borderRadius: 3,
									background:
										"linear-gradient(135deg, #424242 0%, #616161 50%, #757575 100%)",
									border: "3px solid #424242",
									position: "relative",
									overflow: "hidden",
									"&::before": {
										content: '""',
										position: "absolute",
										top: 0,
										left: 0,
										right: 0,
										bottom: 0,
										background:
											"radial-gradient(circle at bottom left, rgba(0,0,0,0.3) 0%, transparent 50%)",
										pointerEvents: "none",
									},
								}}
							>
								<Box sx={{ textAlign: "center", mb: 2 }}>
									<Chip
										icon={<DarkModeIcon />}
										label="20年後のあなた"
										sx={{
											backgroundColor: "#424242",
											color: "white",
											fontWeight: "bold",
											fontSize: "1rem",
											px: 2,
											boxShadow: "0 2px 4px rgba(0,0,0,0.3)",
										}}
									/>
								</Box>
								{futureImage && (
									<Box
										sx={{
											textAlign: "center",
											position: "relative",
										}}
									>
										<img
											src={`data:image/png;base64,${futureImage}`}
											alt="20年後のあなた"
											style={{
												maxWidth: "85%",
												height: "auto",
												borderRadius: 12,
												boxShadow: "0 6px 12px rgba(0,0,0,0.4)",
											}}
										/>
									</Box>
								)}
								<Typography
									variant="body2"
									textAlign="center"
									sx={{
										mt: 2,
										color: "#BDBDBD",
										fontWeight: "medium",
									}}
								>
									喫煙が続いた場合の影響 ⚠️
								</Typography>
							</Paper>
						</Box>
					</Box>
				</Box>

				<Divider sx={{ my: 3 }} />

				{/* 診断レポートセクション */}
				<Box sx={{ mb: 3 }}>
					<Typography
						variant="h6"
						gutterBottom
						sx={{
							fontWeight: "bold",
							color: "#333",
							display: "flex",
							alignItems: "center",
							gap: 1,
						}}
					>
						🏥 診断レポート
					</Typography>
					<Paper
						sx={{
							p: 3,
							backgroundColor: "#F5F5F5",
							borderRadius: 2,
							border: "1px solid #E0E0E0",
						}}
					>
						<Typography
							variant="body1"
							sx={{
								lineHeight: 1.6,
								color: "#333",
							}}
						>
							{diagnosisReport.data.predicted_impact}
						</Typography>
					</Paper>
				</Box>
				{/* 画像解析結果セクション */}
				{imageAnalysisResult && (
					<Box sx={{ mb: 3 }}>
						<Typography
							variant="h6"
							gutterBottom
							sx={{
								fontWeight: "bold",
								color: "#333",
								display: "flex",
								alignItems: "center",
								gap: 1,
							}}
						>
							🔍 画像解析結果
						</Typography>
						<Paper
							sx={{
								p: 3,
								backgroundColor: "#E3F2FD",
								borderRadius: 2,
								border: "1px solid #90CAF9",
							}}
						>
							<Typography
								variant="body1"
								sx={{
									lineHeight: 1.6,
									color: "#0D47A1",
								}}
							>
								{imageAnalysisResult}
							</Typography>
						</Paper>
					</Box>
				)}
				{/* 外見への影響セクション */}
				{diagnosisReport.data.impact_on_appearance && (
					<Box sx={{ mb: 3 }}>
						<Typography
							variant="h6"
							gutterBottom
							sx={{
								fontWeight: "bold",
								color: "#333",
								display: "flex",
								alignItems: "center",
								gap: 1,
							}}
						>
							✨ 外見への影響
						</Typography>
						<Paper
							sx={{
								p: 3,
								backgroundColor: "#FFF3E0",
								borderRadius: 2,
								border: "1px solid #FFB74D",
							}}
						>
							<Typography
								variant="body1"
								sx={{
									lineHeight: 1.6,
									color: "#E65100",
								}}
							>
								{diagnosisReport.data.impact_on_appearance}
							</Typography>
						</Paper>
					</Box>
				)}

				<Divider sx={{ my: 3 }} />

				{/* リセットボタン */}
				<Box sx={{ textAlign: "center" }}>
					<Button
						variant="contained"
						onClick={onClickReset}
						sx={{
							mt: 2,
							px: 4,
							py: 1.5,
							borderRadius: 3,
							background: "linear-gradient(45deg, #FF6B6B 30%, #4ECDC4 90%)",
							fontSize: "1.1rem",
							fontWeight: "bold",
							boxShadow: 3,
							"&:hover": {
								boxShadow: 6,
								transform: "translateY(-2px)",
								transition: "all 0.3s ease",
							},
						}}
					>
						🔄 新しく診断する
					</Button>
				</Box>
			</CardContent>
		</Card>
	);
}

export default ResultDisplay;
