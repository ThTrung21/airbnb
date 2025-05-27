import ReactStars from "react-stars";
import useRating from "@/app/hooks/useRating";
import { SafeUser } from "@/app/types";

interface RatingProps {
  listingId: string;
  currentUser?: SafeUser | null;
  userRating?: number; // from DB, the user's past rating for this listing
}

const RatingStars: React.FC<RatingProps> = ({
  listingId,
  currentUser,
  userRating,
}) => {
  const { handleRatingChange, currentRating } = useRating({
    listingId,
    currentUser,
    currentRating: userRating,
  });

  return (
    <div>
      {currentUser && (
        <ReactStars
          count={5}
          size={30}
          value={currentRating}
          color2="#ffd700"
          onChange={handleRatingChange}
          half={false}
        />
      )}
    </div>
  );
};

export default RatingStars;
