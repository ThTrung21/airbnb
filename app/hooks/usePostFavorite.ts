import axios from "axios";
import { useRouter } from "next/navigation";
import { useCallback, useMemo } from "react";
import toast from "react-hot-toast";
import { SafeUser } from "@/app/types";

import useLoginModal from "./useLoginModal";
import getCurrentUser from "@/app/actions/getCurrentUser";

interface IUseFavorite {
  postId: string;
  currentUser?: SafeUser | null;
}

const usePostFavorite = ({ postId, currentUser }: IUseFavorite) => {
  const router = useRouter();
  const loginModal = useLoginModal();
  const hasFavorited = useMemo(() => {
    const likeList = currentUser?.postLikeIds || [];
    return likeList.includes(postId);
  }, [currentUser, postId]);

  const toggleFavorite = useCallback(
    async (e: React.MouseEvent<HTMLDivElement>) => {
      e.stopPropagation();

      if (!currentUser) {
        return loginModal.onOpen();
      }

      try {
        let request;

        if (hasFavorited) {
          request = () => axios.delete(`/api/postfavorites/${postId}`);
        } else {
          request = () => axios.post(`/api/postfavorites/${postId}`);
        }

        await request();
        router.refresh();
        toast.success("Success!");
      } catch (error) {
        toast.error("Something went wrong!");
      }
    },
    [currentUser, hasFavorited, postId, loginModal, router]
  );

  return {
    hasFavorited,
    toggleFavorite,
  };
};

export default usePostFavorite;
