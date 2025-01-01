"use client";

import { AiFillHeart, AiOutlineHeart } from "react-icons/ai";
import { SafeUser } from "../types";

import usePostFavorite from "../hooks/usePostFavorite";

interface HeartButtonProps {
  postId: string;
  currentUser?: SafeUser | null;
}

const PostHeartButton: React.FC<HeartButtonProps> = ({
  postId,
  currentUser,
}) => {
  const { hasFavorited, toggleFavorite } = usePostFavorite({
    postId,
    currentUser,
  });

  return (
    <div
      onClick={toggleFavorite}
      className="
    relative
    hover:opacity-80
    transition
    cursor-pointer"
    >
      <AiOutlineHeart
        size={28}
        className="
        fill-white
          absolute
          -top-[2px]
          -right-[2px]"
      />
      <AiFillHeart
        size={24}
        className={hasFavorited ? "fill-rose-500" : "fill-neutral-500/70"}
      />
    </div>
  );
};

export default PostHeartButton;
