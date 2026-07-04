import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

const highlights = [
  "FastAPI backend serving crop recommendation APIs",
  "React dashboard for season, state, rainfall, fertilizer, and pesticide inputs",
  "Random Forest model trained on historical crop yield data",
  "Recommendations ranked with crop-relative yield, confidence, and estimated profit",
];

export default function About() {
  return (
    <main className="min-h-screen bg-gray-50 px-6 py-10">
      <section className="mx-auto max-w-5xl space-y-6">
        <div className="rounded-3xl bg-white p-8 shadow-sm">
          <p className="text-sm font-semibold uppercase tracking-wide text-green-700">
            About AgriSense
          </p>
          <h1 className="mt-3 text-4xl font-bold text-gray-950">
            Crop recommendations for data-informed farming decisions.
          </h1>
          <p className="mt-4 max-w-3xl text-lg text-gray-600">
            AgriSense helps compare suitable crops using historical agricultural
            data, seasonal conditions, rainfall, land area, and input usage. It is
            designed as a portfolio-ready full-stack ML project, not as a final
            agronomy advisory system.
          </p>
        </div>

        <div className="grid gap-5 md:grid-cols-2">
          <Card>
            <CardHeader>
              <CardTitle>What It Does</CardTitle>
            </CardHeader>
            <CardContent className="space-y-3 text-gray-600">
              <p>
                Farmers or analysts enter crop year, season, state, area,
                rainfall, fertilizer, and pesticide values. The backend predicts
                yields for historically relevant crops and returns the top
                recommendations.
              </p>
              <p>
                The ranking avoids comparing raw yield alone, because crop yield
                units and scales can differ dramatically.
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Tech Stack</CardTitle>
            </CardHeader>
            <CardContent>
              <ul className="space-y-2 text-gray-600">
                {highlights.map((item) => (
                  <li key={item} className="flex gap-2">
                    <span className="text-green-700">-</span>
                    <span>{item}</span>
                  </li>
                ))}
              </ul>
            </CardContent>
          </Card>
        </div>
      </section>
    </main>
  );
}
