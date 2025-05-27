import { useCallback } from "react";
import { useRouter } from "next/navigation";
import axios from "axios";
import toast from "react-hot-toast";

import useLoginModal from "@/app/hooks/useLoginModal";
import { SafeUser } from "@/app/types";

interface IUseRating {
  listingId: string;
  currentUser?: SafeUser | null;
  currentRating?: number; // user’s previous rating for this listing, if any
}

const useRating = ({
  listingId,
  currentUser,
  currentRating = 0,
}: IUseRating) => {
  const router = useRouter();
  const loginModal = useLoginModal();

  const handleRatingChange = useCallback(
    async (newRating: number) => {
      const roundedRating = Math.round(newRating);
      if (!currentUser) {
        return loginModal.onOpen();
      }

      try {
        await axios.post(`/api/ratings/${listingId}`, {
          stars: roundedRating,
        });

        router.refresh();
        toast.success("Rating submitted!");
      } catch (error) {
        toast.error("Something went wrong while submitting your rating.");
      }
    },
    [currentUser, listingId, loginModal, router]
  );

  return {
    handleRatingChange,
    currentRating,
  };
};

export default useRating;
