class RecommendationController {
    constructor(private nlpService: NLPService) {}

    async getRecommendations(req: Request, res: Response) {
        const keywords = req.body.keywords;
        if (!keywords) {
            return res.status(400).json({ error: 'Keywords are required' });
        }

        try {
            const recommendations = await this.nlpService.getSimilarMovies(keywords);
            return res.status(200).json(recommendations);
        } catch (error) {
            return res.status(500).json({ error: 'An error occurred while fetching recommendations' });
        }
    }
}

export default RecommendationController;