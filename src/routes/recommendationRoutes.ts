import { Router } from 'express';
import { RecommendationController } from '../controllers/recommendationController';

const router = Router();
const recommendationController = new RecommendationController();

export function setRecommendationRoutes(app: Router) {
    app.post('/recommend', recommendationController.getRecommendations.bind(recommendationController));
}

export default router;