import prisma from "@/app/libs/prismadb";

const getUserRating = async (listingId: string, userId?: string | null) => {
  if (!userId) return 0;

  const rating = await prisma.rating.findUnique({
    where: {
      userId_listingId: {
        userId,
        listingId: listingId,
      },
    },
  });

  return rating?.stars ?? 0;
};

export default getUserRating;
