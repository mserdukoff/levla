export default function PassageLoading() {
  return (
    <div className="mx-auto flex min-h-full w-full max-w-[42rem] flex-col px-5 pt-16 sm:px-8">
      <div className="h-3 w-24 rounded bg-rule/80" />
      <div className="mt-8 h-8 w-2/3 rounded bg-rule/80" />
      <div className="mt-10 space-y-3">
        <div className="h-5 w-full rounded bg-rule/60" />
        <div className="h-5 w-11/12 rounded bg-rule/60" />
        <div className="h-5 w-4/5 rounded bg-rule/60" />
      </div>
    </div>
  );
}
