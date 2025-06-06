"use client";
import { useRouter, useSearchParams } from "next/navigation";
import { useCallback } from "react";
import { IconType } from "react-icons";
import qs from "query-string";
import { SafeUser } from "../types";
interface CategoryBoxProps {
  icon: IconType;
  label: string;
  selected?: boolean;
  type: number;
  isFirst?: boolean;
}

const CategoryBox: React.FC<CategoryBoxProps> = ({
  icon: Icon,
  label,
  selected,
  type,
  isFirst,
}) => {
  const router = useRouter();
  const params = useSearchParams();

  const handleClick = useCallback(() => {
    let currentQuery = {};

    if (params) {
      currentQuery = qs.parse(params.toString());
    }

    // If it's the first element of type 2 ("For You"), redirect to recommendation mode
    if (type === 2 && isFirst) {
      if (selected == false) {
        const url = qs.stringifyUrl(
          {
            url: "/",
            query: {
              ...currentQuery,
              recommendation: "true",
            },
          },
          { skipNull: true }
        );
        router.push(url);
        return;
      } else {
        const url = qs.stringifyUrl(
          {
            url: "/",
          },
          { skipNull: true }
        );
        router.push(url);
        return;
      }
    }

    // Otherwise, toggle category selection
    const updatedQuery: any = {
      ...currentQuery,
      category: label,
    };

    // Toggle off if this category is already selected
    if (params?.get("category") === label) {
      delete updatedQuery.category;
    }

    // Clear recommendation if selecting any other category
    delete updatedQuery.recommendation;

    const url = qs.stringifyUrl(
      {
        url: "/",
        query: updatedQuery,
      },
      { skipNull: true }
    );

    router.push(url);
  }, [label, params, router, type, isFirst]);

  const isActive = selected;

  return (
    <div
      onClick={handleClick}
      className={`
        flex
        flex-col
        items-center
        justify-center
        gap-2
        p-3
        border-b-2
        hover:text-neutral-800
        transition
        cursor-pointer
        ${isActive ? "border-b-neutral-800" : "border-transparent"}
        ${isActive ? "text-neutral-800" : "text-neutral-500"}
      `}
    >
      <Icon size={26} />
      <div className="font-medium text-sm">{label}</div>
    </div>
  );
};
export default CategoryBox;
