import React, { useState } from "react";
import {
	Button,
	Box,
	Typography,
	Alert,
	CircularProgress,
	Card,
	CardContent,
} from "@mui/material";
import { fetchHelloWorld, ApiError } from "../services/api";
import type { HelloWorldResponse } from "../services/api";

interface HelloWorldButtonProps {
	/**
	 * ボタンのバリアント
	 */
	variant?: "text" | "outlined" | "contained";
	/**
	 * ボタンのサイズ
	 */
	size?: "small" | "medium" | "large";
}

const HelloWorldButton: React.FC<HelloWorldButtonProps> = ({
	variant = "contained",
	size = "large",
}) => {
	const [loading, setLoading] = useState<boolean>(false);
	const [response, setResponse] = useState<HelloWorldResponse | null>(null);
	const [error, setError] = useState<string | null>(null);

	/**
	 * Hello World APIを呼び出す処理
	 */
	const handleFetchHelloWorld = async () => {
		setLoading(true);
		setError(null);
		setResponse(null);

		try {
			const result = await fetchHelloWorld();
			setResponse(result);
		} catch (err) {
			if (err instanceof Error) {
				setError(err.message);
			} else {
				setError("予期しないエラーが発生しました");
			}
			console.error("Hello World API call failed:", err);
		} finally {
			setLoading(false);
		}
	};

	/**
	 * 結果をクリアする処理
	 */
	const handleClearResult = () => {
		setResponse(null);
		setError(null);
	};

	return (
		<Box sx={{ textAlign: "center", p: 2 }}>
			{/* ボタンエリア */}
			<Box sx={{ mb: 3 }}>
				<Button
					variant={variant}
					size={size}
					onClick={handleFetchHelloWorld}
					disabled={loading}
					sx={{ minWidth: 200, position: "relative" }}
				>
					{loading ? (
						<>
							<CircularProgress size={20} sx={{ mr: 1 }} color="inherit" />
							読み込み中...
						</>
					) : (
						"Hello World API呼び出し"
					)}
				</Button>

				{(response || error) && (
					<Button
						variant="outlined"
						size="small"
						onClick={handleClearResult}
						sx={{ ml: 2 }}
					>
						クリア
					</Button>
				)}
			</Box>

			{/* レスポンス表示エリア */}
			{response && (
				<Card sx={{ maxWidth: 600, margin: "0 auto", mb: 2 }}>
					<CardContent>
						<Typography variant="h6" color="primary" gutterBottom>
							API レスポンス
						</Typography>
						<Typography variant="body1" sx={{ fontWeight: "bold" }}>
							{response.message}
						</Typography>
					</CardContent>
				</Card>
			)}

			{/* エラー表示エリア */}
			{error && (
				<Alert severity="error" sx={{ maxWidth: 600, margin: "0 auto" }}>
					<Typography variant="body2">
						<strong>エラー:</strong> {error}
					</Typography>
				</Alert>
			)}
		</Box>
	);
};

export default HelloWorldButton;
