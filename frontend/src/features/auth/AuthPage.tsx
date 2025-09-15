import AuthForm from "./AuthForm";

const AuthPage = () => {
  return (
    <main className="min-h-screen w-full grid grid-cols-2 gap-4 p-8">
      <section className="flex flex-col justify-center items-center container  mx-auto">
        <div className="max-w-md w-full">
          <h1 className="text-2xl font-bold mb-4">Welcome Back!</h1>
          <h4 className="text-lg mb-4 max-w-prose">
            Today is a new day. It's your day. You shape it. Sign in to start
            searching your clothes.
          </h4>
          <AuthForm />
        </div>
      </section>
      <div>
        <img
          src="/auth_bg.jpg"
          alt="Authentication background - modern workspace"
          className="w-full h-full object-cover rounded-2xl"
          loading="lazy"
        />
      </div>
    </main>
  );
};

export default AuthPage;
