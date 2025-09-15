import { z } from "zod";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import LoginForm from "./LoginForm";
import RegisterForm from "./RegisterForm";
import { Button } from "@/components/ui/button";
import { FaFacebook, FaGoogle } from "react-icons/fa";
import { FaSquareXTwitter } from "react-icons/fa6";
import { useAuthStore } from "@/stores/useAuthStore";
import { useNavigate } from "@tanstack/react-router";
import { useOAuth } from "@/hooks/useOAuth";
import { useLogin, useRegister } from "@/hooks/useAuth";

const RegisterFormSchema = z.object({
  firstName: z.string().min(1, { message: "Required" }),
  lastName: z.string().min(1, { message: "Required" }),
  email: z.email({ message: "Invalid email" }),
  password: z.string().min(1, { message: "Required" }),
  confirmPassword: z.string().min(1, { message: "Required" }),
});

const LoginFormSchema = z.object({
  email: z.email({ message: "Invalid email" }),
  password: z.string().min(1, { message: "Required" }),
});

const AuthForm = () => {
  const navigate = useNavigate();
  const { login } = useAuthStore();
  const { initiateGoogleOAuth, isLoading } = useOAuth();
  const { isLoginPending, login: mutateLogin } = useLogin();
  const { register: mutateRegister } = useRegister();

  const onLoginSubmit = async (values: z.infer<typeof LoginFormSchema>) => {
    console.log("Login:", values);
    try {
      const response = await mutateLogin(values);

      if (response.data) {
        const { user_data, access_token, refresh_token } = response.data;
        login(access_token, refresh_token, user_data!);
        navigate({ to: "/dashboard" });
        console.log("Login Response:", { user_data });
      } else {
        console.error("No data found in the response");
      }
    } catch (error) {
      console.error("Login/Register Error:", error);
    }
  };

  const onRegisterSubmit = async (
    values: z.infer<typeof RegisterFormSchema>
  ) => {
    console.log("Register:", values);
    try {
      const response = await mutateRegister({
        first_name: values.firstName,
        last_name: values.lastName,
        email: values.email,
        password: values.password,
      });

      if (response.status === "success") {
        navigate({ to: "/dashboard" });
        console.log("Register Response:", response);
      } else {
        console.error("No data found in the response");
      }
    } catch (error) {
      console.error("Login/Register Error:", error);
    }
  };

  return (
    <>
      <section className="flex flex-col justify-center rounded-md gap-4">
        <Tabs defaultValue="login">
          <TabsList className="grid grid-cols-2 gap-2 bg-gray-300">
            <TabsTrigger value="login">Login</TabsTrigger>
            <TabsTrigger value="register">Register</TabsTrigger>
          </TabsList>
          <TabsContent value="login">
            <LoginForm onSubmit={onLoginSubmit} isPending={isLoginPending} />
          </TabsContent>
          <TabsContent value="register">
            <RegisterForm onSubmit={onRegisterSubmit} />
          </TabsContent>
        </Tabs>

        <div className="flex items-center w-full">
          <div className="flex-1 border-t border-gray-300"></div>
          <span className="px-4 text-sm text-gray-500">Or</span>
          <div className="flex-1 border-t border-gray-300"></div>
        </div>

        <Button
          className="text-black bg-blue-100"
          variant={"secondary"}
          onClick={initiateGoogleOAuth}
          disabled={isLoading}
        >
          <FaGoogle size={20} />
          Login With Google
        </Button>
        <Button className="text-white bg-blue-600">
          <FaFacebook size={20} />
          Login With Facebook
        </Button>
        <Button className="text-white bg-black">
          <FaSquareXTwitter size={20} />
          Login With Twitter
        </Button>
      </section>
    </>
  );
};

export default AuthForm;
