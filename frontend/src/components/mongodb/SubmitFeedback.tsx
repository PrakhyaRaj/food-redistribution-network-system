import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { Star } from "lucide-react";

const API_BASE = "http://127.0.0.1:5000";

export const SubmitFeedback = ({ onSuccess }: { onSuccess: () => void }) => {
  const [rating, setRating] = useState(0);
  const [content, setContent] = useState("");
  const [feedbackType, setFeedbackType] = useState("suggestion");
  const [loading, setLoading] = useState(false);

  const submit = async () => {
    if (!rating || !content.trim()) return;

    setLoading(true);
    try {
      const token = localStorage.getItem("token");
      const res = await fetch(`${API_BASE}/feedback/submit`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          ...(token && { "Authorization": `Bearer ${token}` }),
        },
        body: JSON.stringify({
          user_id: localStorage.getItem("user_id"),
          message: content,
          metadata: {
           rating,
           feedback_type: feedbackType,
           food_id: 0,
          },
        }),
      });

      if (res.ok) {
        setRating(0);
        setContent("");
        setFeedbackType("suggestion");
        onSuccess();
      } else {
        const errorData = await res.json().catch(() => ({}));
        console.error("Failed to submit feedback:", errorData);
        alert("Failed to submit feedback");
      }
    } catch (err) {
      console.error(err);
      alert("Failed to submit feedback");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="p-4 border rounded-lg bg-white space-y-4">
      <h3 className="font-semibold">Write Feedback</h3>

      {/* Star Rating */}
      <div className="space-y-2">
        <label className="text-sm font-medium">Rating</label>
        <div className="flex gap-2">
          {[1, 2, 3, 4, 5].map((s) => (
            <Star
              key={s}
              className={`h-6 w-6 cursor-pointer ${
                s <= rating ? "fill-yellow-400 text-yellow-400" : "text-gray-300"
              }`}
              onClick={() => setRating(s)}
            />
          ))}
        </div>
      </div>

      {/* Feedback Type */}
      <div className="space-y-2">
        <label className="text-sm font-medium">Feedback Type</label>
        <select
          value={feedbackType}
          onChange={(e) => setFeedbackType(e.target.value)}
          className="w-full p-2 border rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
        >
          <option value="praise">Praise</option>
          <option value="suggestion">Suggestion</option>
          <option value="bug">Bug</option>
          <option value="complaint">Complaint</option>
        </select>
      </div>

      {/* Feedback Content */}
      <div className="space-y-2">
        <label className="text-sm font-medium">Your Feedback</label>
        <Textarea
          placeholder="Enter your detailed feedback here..."
          value={content}
          onChange={(e) => setContent(e.target.value)}
          className="min-h-[100px]"
        />
      </div>

      {/* Submit Button */}
      <Button
        onClick={submit}
        disabled={loading || rating === 0 || !content.trim()}
        className="w-full"
      >
        {loading ? "Submitting..." : "Submit Feedback"}
      </Button>
    </div>
  );
};
