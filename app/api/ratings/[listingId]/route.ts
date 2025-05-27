import { NextResponse } from "next/server";
import getCurrentUser from "@/app/actions/getCurrentUser";
import prisma from "@/app/libs/prismadb";

interface IParams {
  listingId?: string;
}

export async function POST(request: Request, { params }: { params: IParams }) {
  const currentUser = await getCurrentUser();
  if (!currentUser) return NextResponse.error();

  const { listingId } = params;
  if (!listingId || typeof listingId !== "string") {
    throw new Error("Invalid ID");
  }

  const body = await request.json();
  const { stars } = body;

  if (!stars || stars < 1 || stars > 5) {
    return NextResponse.json(
      { error: "Rating must be between 1 and 5" },
      { status: 400 }
    );
  }

  // Upsert (update if exists, create if not)
  const rating = await prisma.rating.upsert({
    where: {
      userId_listingId: {
        userId: currentUser.id,
        listingId: listingId,
      },
    },
    update: {
      stars,
    },
    create: {
      userId: currentUser.id,
      listingId: listingId,
      stars,
    },
  });

  return NextResponse.json(rating);
}
