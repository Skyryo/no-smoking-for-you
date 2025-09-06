import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import ImageUploader from "./src/components/ImageUploader";
import ProcessingStatus from "./src/components/ProcessingStatus";
import QuestionnaireForm from "./src/components/QuestionnaireForm";
import ResultDisplay from "./src/components/ResultDisplay";

function App() {
	return (
		<BrowserRouter>
			<Routes>
				<Route path="/upload" element={<ImageUploader />} />
				<Route path="/status" element={<ProcessingStatus />} />
				<Route path="/questionnaire" element={<QuestionnaireForm />} />
				<Route path="/result" element={<ResultDisplay />} />
				<Route path="*" element={<Navigate to="/upload" replace />} />
			</Routes>
		</BrowserRouter>
	);
}

export default App;
