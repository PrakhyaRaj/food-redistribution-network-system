import React, { useState } from "react";
import { SubmitFeedback } from "@/components/mongodb/SubmitFeedback";
import { FeedbackInsights } from "@/components/mongodb/FeedbackInsights";
import { toast } from "sonner";

export const HomepageFeedback: React.FC = () => {
  const [reloadFeedback, setReloadFeedback] = useState(false);

  const handleSuccess = () => {
    setReloadFeedback(prev => !prev); // refresh insights
    toast.success("Feedback submitted successfully!");
  };

  return (
    <div className="max-w-4xl mx-auto p-4 space-y-8">
      {/* Submit Feedback Card */}
      <div className="bg-white p-6 rounded-xl border shadow-md">
        <h2 className="text-2xl font-bold mb-4 flex items-center gap-2">
          <span className="text-xl">💬</span> Give Feedback
        </h2>
        <p className="text-muted-foreground mb-4">
          Share your experience or suggestions to help improve the platform.
        </p>
        <SubmitFeedback onSuccess={handleSuccess} />
      </div>

      {/* Feedback Insights Card */}
      <div className="bg-white p-6 rounded-xl border shadow-md">
        <FeedbackInsights key={reloadFeedback ? "reload" : "normal"} reloadSignal={reloadFeedback} />
      </div>
    </div>
  );
};
