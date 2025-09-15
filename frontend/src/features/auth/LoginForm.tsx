import { Button } from "@/components/ui/button";
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "@/components/ui/form";
import { Input } from "@/components/ui/input";
import { zodResolver } from "@hookform/resolvers/zod";
import { Link } from "@tanstack/react-router";
import { useForm } from "react-hook-form";
import { FaCircle } from "react-icons/fa";
import z from "zod";

interface LoginFormProps {
  onSubmit: (values: LoginFormValues) => void;
  isPending: boolean;
}

interface LoginFormValues {
  email: string;
  password: string;
}

const LoginFormSchema = z.object({
  email: z.string().email({ message: "Invalid email" }),
  password: z.string().min(1, { message: "Required" }),
});

const LoginForm = ({ onSubmit, isPending }: LoginFormProps) => {
  const loginForm = useForm<z.infer<typeof LoginFormSchema>>({
    resolver: zodResolver(LoginFormSchema),
    defaultValues: {
      email: "",
      password: "",
    },
  });

  return (
    <Form {...loginForm}>
      <form onSubmit={loginForm.handleSubmit(onSubmit)} className="space-y-2">
        <FormField
          control={loginForm.control}
          name="email"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Email</FormLabel>
              <FormControl>
                <Input
                  type="email"
                  placeholder="Enter your email"
                  {...field}
                  className="border-black/25 bg-blue-200/15"
                />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />
        <FormField
          control={loginForm.control}
          name="password"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Password</FormLabel>
              <FormControl>
                <Input
                  type="password"
                  placeholder="Enter your password"
                  {...field}
                  className="border-black/25 bg-blue-200/15"
                />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />
        <Link to="/auth" className="flex justify-end text-blue-700">
          Forgot Password?
        </Link>
        <Button
          type="submit"
          className="w-full bg-[#162D3A] h-[52px] text-white hover:bg-gray-900 rounded-xl"
        >
          {isPending && <FaCircle className="mr-2 h-4 w-4 animate-spin" />}
          {isPending ? "Logging in..." : "Login"}
        </Button>
      </form>
    </Form>
  );
};

export default LoginForm;
