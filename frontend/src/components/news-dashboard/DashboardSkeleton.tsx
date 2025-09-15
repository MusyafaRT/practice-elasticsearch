import { Skeleton } from "../ui/skeleton";

const NewsDashboardSkeleton = () => {
  return (
    <section className="px-6 flex flex-col gap-4">
      {/* Statistic card skeleton */}
      <div className="grid grid-cols-12 gap-6 my-3">
        <div className="col-span-12">
          <div className="h-[120px] w-full rounded-xl border p-6 flex flex-col gap-4">
            <div className="flex flex-col gap-2">
              <Skeleton className="h-6 w-1/4" />
              <Skeleton className="h-4 w-1/3" />
            </div>
            <div className="flex-1">
              <Skeleton className="h-full w-full" />
            </div>
          </div>
        </div>

        {/* Timeline skeleton */}
        <div className="col-span-8">
          <div className="h-[388px] w-full rounded-xl border p-6 flex flex-col gap-4">
            <div className="flex flex-col gap-2">
              <Skeleton className="h-6 w-1/4" />
              <Skeleton className="h-4 w-1/3" />
            </div>
            <div className="flex-1">
              <Skeleton className="h-full w-full" />
            </div>
          </div>
        </div>

        {/* Recent news skeleton */}
        <div className="col-span-4 row-span-2">
          <div className="h-full w-full rounded-xl border p-6 flex flex-col gap-4">
            <div className="flex flex-col gap-2">
              <Skeleton className="h-6 w-1/4" />
              <Skeleton className="h-4 w-1/3" />
            </div>
            <div className="flex-1">
              <Skeleton className="h-full w-full" />
            </div>
          </div>
        </div>

        {/* Tag distribution skeleton */}
        <div className="col-span-8">
          <div className="h-[388px] w-full rounded-xl border p-6 flex flex-col gap-4">
            <div className="flex flex-col gap-2">
              <Skeleton className="h-6 w-1/4" />
              <Skeleton className="h-4 w-1/3" />
            </div>
            <div className="flex-1">
              <Skeleton className="h-full w-full" />
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};

export default NewsDashboardSkeleton;
