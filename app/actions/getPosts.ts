import prisma from "@/app/libs/prismadb";

export interface IPostParams {
  userId?: string;
  searchQuery?: string;
}

export default async function getPosts(params: IPostParams) {
  try {
    const { userId, searchQuery } = params;

    let query: any = {};

    if (searchQuery) {
      query.searchQuery = searchQuery;
    }

    const posts = await prisma.post.findMany({
      where: query,
      orderBy: {
        id: "asc",
      },
    });

    return posts;
  } catch (error: any) {
    throw new Error(error);
  }
}
