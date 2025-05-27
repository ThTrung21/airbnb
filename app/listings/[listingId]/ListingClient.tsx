"use client";

import Container from "@/app/components/Container";
import useLoginModal from "@/app/hooks/useLoginModal";
import ListingHead from "@/app/components/listings/ListingHead";
import ListingInfo from "@/app/components/listings/ListingInfo";
import ListingReservation from "@/app/components/listings/ListingReservation";
import { categories } from "@/app/components/navbar/Categories";
import { SafeListing, SafeReservation, SafeUser } from "@/app/types";

import RatingStars from "@/app/components/inputs/RatingStars";
import getUserRating from "@/app/actions/getUserRating";

import axios from "axios";
import {
  differenceInCalendarDays,
  differenceInDays,
  eachDayOfInterval,
} from "date-fns";
import { useRouter } from "next/navigation";
import { useCallback, useEffect, useMemo, useState } from "react";
import { Range } from "react-date-range";
import toast from "react-hot-toast";
import { loadStripe } from "@stripe/stripe-js";
const initialDateRange = {
  startDate: new Date(),
  endDate: new Date(),
  key: "selection",
};
interface ListingClientProps {
  reservations?: SafeReservation[];
  listing: SafeListing & {
    user: SafeUser;
  };
  currentUser: SafeUser | null;
  userRating?: number;
}
const stripePromise = loadStripe(
  process.env.NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY as string
);
const ListingClient: React.FC<ListingClientProps> = ({
  listing,
  reservations = [],
  currentUser,
  userRating = 0, // default 0
}) => {
  const loginModal = useLoginModal();
  const router = useRouter();

  //get dates that property has already been booked and disable them
  const disabledDates = useMemo(() => {
    let dates: Date[] = [];
    reservations.forEach((reservation) => {
      const range = eachDayOfInterval({
        start: new Date(reservation.startDate),
        end: new Date(reservation.endDate),
      });

      dates = [...dates, ...range];
    });
    return dates;
  }, [reservations]);

  const [isLoading, setIsLoading] = useState(false);
  const [totalPrice, setTotalPrice] = useState(listing.price);
  const [dateRange, setDateRange] = useState<Range>(initialDateRange);

  //simple rating
  //const { hasRated, doRating } = useRating()

  const onCreateReservationNoPay = useCallback(() => {
    if (!currentUser) return loginModal.onOpen();
    console.log("start date: ", dateRange.startDate);
    console.log("end date: ", dateRange.endDate);
    console.log(listing?.id);
    console.log(totalPrice);
    setIsLoading(true);

    axios
      .post("/api/reservations", {
        totalPrice,
        startDate: dateRange.startDate,
        endDate: dateRange.endDate,
        listingId: listing?.id,
        isPaid: false,
      })
      .then(() => {
        toast.success("Listing reserved!");
        setDateRange(initialDateRange);
        router.push("/trips");
        router.refresh();
      })
      .catch(() => {
        toast.error("Something went wrong.");
      })
      .finally(() => {
        setIsLoading(false);
      });
  }, [totalPrice, dateRange, listing?.id, router, currentUser, loginModal]);

  const onCreateReservation = useCallback(async () => {
    if (!currentUser) return loginModal.onOpen();

    console.log("start date: ", dateRange.startDate);
    console.log("end date: ", dateRange.endDate);
    console.log(listing?.id);
    console.log(totalPrice);

    setIsLoading(true);

    try {
      // Create a reservation in your app's database
      await axios.post("/api/reservations", {
        totalPrice,
        startDate: dateRange.startDate,
        endDate: dateRange.endDate,
        listingId: listing?.id,
        isPaid: true,
      });

      // Create a Stripe Checkout session
      const stripe = await stripePromise;
      if (!stripe) throw new Error("Stripe not loaded");

      const response = await axios.post("/api/create-checkout-sessions", {
        amount: totalPrice,
        dateRange,
        listingId: listing?.id,
        name: listing?.title,
      });

      const { sessionId } = response.data;

      if (sessionId) {
        await stripe.redirectToCheckout({ sessionId });
      } else {
        throw new Error("Failed to create Stripe Checkout session");
      }
    } catch (error) {
      console.error(error);
      toast.error("Something went wrong.");
    } finally {
      setIsLoading(false);
      toast.success("Booking complete!");
    }
  }, [
    totalPrice,
    dateRange,
    listing?.id,
    currentUser,
    loginModal,
    listing?.title,
  ]);
  const category = useMemo(() => {
    return categories.find((item) => item.label === listing.category);
  }, [listing.category]);

  //calculate price for trip based on reserved nights
  useEffect(() => {
    if (dateRange.startDate && dateRange.endDate) {
      const dayCount = differenceInCalendarDays(
        dateRange.endDate,
        dateRange.startDate
      );
      if (dayCount && listing.price) {
        setTotalPrice(dayCount * listing.price);
      } else {
        setTotalPrice(listing.price);
      }
    }
  }, [dateRange, listing.price]);

  return (
    <Container>
      <div className="max-w-screen-lg mx-auto">
        <div className="flex flex-col gap-6">
          <ListingHead
            title={listing.title}
            imageSrc={listing.imageSrc}
            locationValue={listing.locationValue}
            id={listing.id}
            currentUser={currentUser}
          />
          <div className="grid grid-cols-1 md:grid-cols-7 md:gap-10 mt-6">
            <ListingInfo
              user={listing.user}
              category={category}
              description={listing.description}
              address={listing.address}
              roomCount={listing.roomCount}
              guestCount={listing.guestCount}
              bathroomCount={listing.bathroomCount}
              locationValue={listing.locationValue}
            />
            <div className="order-first mb-10 mb:order-last md:col-span-3">
              {currentUser && (
                <RatingStars
                  // className="mb-2px size-1 "
                  listingId={listing.id}
                  currentUser={currentUser}
                  userRating={userRating}
                />
              )}
              <ListingReservation
                currentUser={currentUser}
                price={listing.price}
                totalPrice={totalPrice}
                onChangeDate={(value) => setDateRange(value)}
                dateRange={dateRange}
                onSubmitMain={onCreateReservation}
                onSubmitSecondary={onCreateReservationNoPay}
                disabled={isLoading}
                disabledDates={disabledDates}
              />
            </div>
          </div>
        </div>
      </div>
    </Container>
  );
};

export default ListingClient;
