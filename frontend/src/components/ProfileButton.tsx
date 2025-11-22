import { Link } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { User } from "lucide-react";

const ProfileButton = () => {
  return (
    <Button variant="outline" size="sm" asChild >
      <Link to="/profile">
        <User className="h-4 w-4 mr-2" />
        Profile
      </Link>
    </Button>
  );
};

export default ProfileButton;
