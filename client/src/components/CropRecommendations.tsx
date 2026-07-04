import type { RecommendResponse } from "@/lib/api-types";

interface CropRecommendationsProps {
  data: RecommendResponse;
}

const CropRecommendations = ({ data }: CropRecommendationsProps) => {
  return (
    <div className="grid gap-4 p-4 md:grid-cols-2 lg:grid-cols-3">
      {data.recommendations.map((item) => (
        <div
          key={item.rank}
          className="rounded-xl border bg-white p-4 shadow transition-all hover:shadow-lg"
        >
          <h2 className="text-xl font-semibold">
            #{item.rank} {item.crop}
          </h2>

          <div className="mt-3 space-y-1 text-sm text-gray-700">
            <p>
              <strong>Predicted Yield:</strong> {item.estimated_yield}
            </p>
            <p>
              <strong>Estimated Profit:</strong> Rs. {item.estimated_profit}
            </p>
            <p>
              <strong>Confidence:</strong> {item.confidence}%
            </p>
            <p>
              <strong>Yield Range:</strong> {item.min_yield} - {item.max_yield}
            </p>
            <p>
              <strong>Yield Index:</strong> {item.yield_index}x crop median
            </p>
            <p>
              <strong>Suitability Score:</strong> {item.recommendation_score}
            </p>
          </div>
        </div>
      ))}
    </div>
  );
};

export default CropRecommendations;
