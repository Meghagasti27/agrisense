import { useState, type ChangeEvent } from "react";
import { useAuth } from "@clerk/clerk-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import type { RecommendResponse } from "@/lib/api-types";
import CropRecommendations from "./CropRecommendations";

const API_BASE_URL =
  import.meta.env.VITE_API_URL ||
  import.meta.env.VITE_BACKEND_URL ||
  "http://localhost:8000";

const seasons = ["Autumn", "Kharif", "Rabi", "Summer", "Whole Year", "Winter"];

const states = [
  "Andhra Pradesh",
  "Arunachal Pradesh",
  "Assam",
  "Bihar",
  "Chhattisgarh",
  "Delhi",
  "Goa",
  "Gujarat",
  "Haryana",
  "Himachal Pradesh",
  "Jammu and Kashmir",
  "Jharkhand",
  "Karnataka",
  "Kerala",
  "Madhya Pradesh",
  "Maharashtra",
  "Manipur",
  "Meghalaya",
  "Mizoram",
  "Nagaland",
  "Odisha",
  "Puducherry",
  "Punjab",
  "Sikkim",
  "Tamil Nadu",
  "Telangana",
  "Tripura",
  "Uttar Pradesh",
  "Uttarakhand",
  "West Bengal",
];

const initialForm = {
  crop_year: "2020",
  season: "",
  state: "",
  area: "",
  annual_rainfall: "",
  fertilizer: "",
  pesticide: "",
};

function Dashboard() {
  const { getToken } = useAuth();
  const [formData, setFormData] = useState(initialForm);
  const [result, setResult] = useState<RecommendResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleInputChange = (event: ChangeEvent<HTMLInputElement>) => {
    const { name, value } = event.target;
    setFormData((previous) => ({ ...previous, [name]: value }));
  };

  const updateSelect = (name: keyof typeof initialForm, value: string) => {
    setFormData((previous) => ({ ...previous, [name]: value }));
  };

  const validateForm = () => {
    const required = Object.values(formData);
    if (required.some((value) => value === "")) {
      return "Please complete all fields.";
    }

    const numericFields = [
      ["Area", Number(formData.area)],
      ["Annual rainfall", Number(formData.annual_rainfall)],
      ["Fertilizer", Number(formData.fertilizer)],
      ["Pesticide", Number(formData.pesticide)],
    ] as const;

    const invalidField = numericFields.find(([, value]) => !Number.isFinite(value) || value < 0);
    if (invalidField) {
      return `${invalidField[0]} must be a valid non-negative number.`;
    }

    return null;
  };

  const predict = async () => {
    const validationError = validateForm();
    if (validationError) {
      setError(validationError);
      return;
    }

    setLoading(true);
    setError(null);
    setResult(null);

    const controller = new AbortController();
    const timeout = window.setTimeout(() => controller.abort(), 20000);

    try {
      const token = await getToken();
      const payload = {
        crop_year: Number(formData.crop_year),
        season: formData.season,
        state: formData.state,
        area: Number(formData.area),
        annual_rainfall: Number(formData.annual_rainfall),
        fertilizer: Number(formData.fertilizer),
        pesticide: Number(formData.pesticide),
      };

      const response = await fetch(`${API_BASE_URL}/api/recommend`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          ...(token ? { Authorization: `Bearer ${token}` } : {}),
        },
        body: JSON.stringify(payload),
        signal: controller.signal,
      });

      const data = await response.json();
      if (!response.ok) {
        throw new Error(data.detail || "The prediction service returned an error.");
      }

      setResult(data as RecommendResponse);
    } catch (requestError) {
      setError(
        requestError instanceof DOMException && requestError.name === "AbortError"
          ? "Prediction timed out. Please try again."
          : requestError instanceof Error
            ? requestError.message
            : "Failed to get a recommendation.",
      );
    } finally {
      window.clearTimeout(timeout);
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 px-3 py-10">
      <div className="mx-auto max-w-6xl">
        <Card>
          <CardHeader>
            <CardTitle className="text-2xl">Crop Recommendation System</CardTitle>
          </CardHeader>

          <CardContent>
            <div className="grid grid-cols-1 gap-6 md:grid-cols-2">
              <div className="space-y-2">
                <Label htmlFor="crop_year">Crop Year</Label>
                <Select value={formData.crop_year} onValueChange={(value) => updateSelect("crop_year", value)}>
                  <SelectTrigger id="crop_year">
                    <SelectValue placeholder="Select Year" />
                  </SelectTrigger>
                  <SelectContent>
                    {Array.from({ length: 24 }, (_, index) => 1997 + index).map((year) => (
                      <SelectItem key={year} value={year.toString()}>
                        {year}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              <div className="space-y-2">
                <Label htmlFor="season">Season</Label>
                <Select value={formData.season} onValueChange={(value) => updateSelect("season", value)}>
                  <SelectTrigger id="season">
                    <SelectValue placeholder="Select Season" />
                  </SelectTrigger>
                  <SelectContent>
                    {seasons.map((season) => (
                      <SelectItem key={season} value={season}>
                        {season}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              <div className="space-y-2">
                <Label htmlFor="state">State</Label>
                <Select value={formData.state} onValueChange={(value) => updateSelect("state", value)}>
                  <SelectTrigger id="state">
                    <SelectValue placeholder="Select State" />
                  </SelectTrigger>
                  <SelectContent>
                    {states.map((state) => (
                      <SelectItem key={state} value={state}>
                        {state}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              <div className="space-y-2">
                <Label htmlFor="area">Area (Hectares)</Label>
                <Input
                id="area"
                name="area"
                type="number"
                min="0"
                placeholder="e.g. 500"
                value={formData.area}
                onChange={handleInputChange}
                />
                <p className="text-xs text-gray-500">Total cultivated land area in hectares.</p>
              </div>

              <div className="space-y-2">
                <Label htmlFor="annual_rainfall">
  Annual Rainfall (mm/year)
</Label>

<Input
  id="annual_rainfall"
  name="annual_rainfall"
  type="number"
  min="0"
  placeholder="e.g. 1000"
  value={formData.annual_rainfall}
  onChange={handleInputChange}
/>

<p className="text-xs text-gray-500">
  Average annual rainfall in millimeters.
</p>
              </div>

              <div className="space-y-2">
                <Label htmlFor="fertilizer">
  Fertilizer Usage (kg)
</Label>

<Input
  id="fertilizer"
  name="fertilizer"
  type="number"
  min="0"
  placeholder="e.g. 1995"
  value={formData.fertilizer}
  onChange={handleInputChange}
/>

<p className="text-xs text-gray-500">
  Total fertilizer applied in kilograms.
</p>
              </div>

              <div className="space-y-2">
                <Label htmlFor="pesticide">
  Pesticide Usage (kg)
</Label>

<Input
  id="pesticide"
  name="pesticide"
  type="number"
  min="0"
  placeholder="e.g. 2000"
  value={formData.pesticide}
  onChange={handleInputChange}
/>

<p className="text-xs text-gray-500">
  Total pesticide applied in kilograms.
</p>
              </div>
            </div>

            {error && (
              <div role="alert" className="mt-5 rounded-md border border-red-200 bg-red-50 p-3 text-sm text-red-700">
                {error}
              </div>
            )}

            <div className="mt-6 flex">
              <Button onClick={predict} disabled={loading} className="mx-auto max-w-[60vw] flex-1">
                {loading ? "Getting Recommendation..." : "Get Prediction"}
              </Button>
            </div>

            {result && (
              <Card className="mt-6 bg-blue-50">
                <CardHeader>
                  <CardTitle className="text-lg">Recommendation Result</CardTitle>
                </CardHeader>
                <CardContent>
                  <CropRecommendations data={result} />
                </CardContent>
              </Card>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}

export default Dashboard;
