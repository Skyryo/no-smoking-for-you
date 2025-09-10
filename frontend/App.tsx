import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import ImageUploader from "./src/components/ImageUploader";
import ProcessingStatus from "./src/components/ProcessingStatus";
import QuestionnaireForm from "./src/components/QuestionnaireForm";
import ResultDisplay from "./src/components/ResultDisplay";

const handleUploadSuccess = (result: any) => {
  console.log("Upload successful:", result);
};

const handleUploadError = (error: any) => {
  console.error("Upload error:", error);
};

function App() {
	return (
		<BrowserRouter>
			<Routes>
				<Route path="/upload" element={<ImageUploader onUploadSuccess={handleUploadSuccess} onUploadError={handleUploadError} />} />
				<Route path="/status" element={<ProcessingStatus />} />
				<Route path="/questionnaire" element={<QuestionnaireForm />} />
				<Route path="/result" element={<ResultDisplay />} />
				<Route path="*" element={<Navigate to="/upload" replace />} />
			</Routes>
		</BrowserRouter>
	);
}

export default App;
