import Stripe from "stripe";
import { NextResponse } from "next/server";
import { format } from "date-fns";
const stripe = new Stripe(process.env.STRIPE_SECRET_KEY as string, {
  apiVersion: "2024-12-18.acacia",
});

export async function POST(req: Request) {
  const { amount, dateRange, listingId, name } = await req.json();

  try {
    const session = await stripe.checkout.sessions.create({
      payment_method_types: ["card"],
      mode: "payment",
      line_items: [
        {
          price_data: {
            currency: "usd",
            product_data: {
              name: `Reservation for listing ${name}`,
              description: `From ${format(
                dateRange.startDate,
                "PP"
              )} to ${format(dateRange.endDate, "PP")}`,
            },
            unit_amount: amount * 100, // Convert amount to cents
          },
          quantity: 1,
        },
      ],
      success_url: `${process.env.NEXT_PUBLIC_BASE_URL}/trips`,
      cancel_url: `${process.env.NEXT_PUBLIC_BASE_URL}`,
    });

    return NextResponse.json({ sessionId: session.id });
  } catch (error: any) {
    return NextResponse.json({ error: error.message }, { status: 500 });
  }
}
