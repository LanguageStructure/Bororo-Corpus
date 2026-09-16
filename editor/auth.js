import NextAuth from 'next-auth';
import GitHub from 'next-auth/providers/github';

const allowedLogin = (process.env.CORBO_EDITOR_GITHUB_LOGIN || 'LanguageStructure').toLocaleLowerCase('en-US');

export const { handlers, auth, signIn, signOut } = NextAuth({
  providers: [GitHub],
  callbacks: {
    authorized({ auth }) {
      const login = auth?.user?.login || auth?.user?.name || '';
      return login.toLocaleLowerCase('en-US') === allowedLogin;
    },
    async jwt({ token, profile }) {
      if (profile?.login) token.login = profile.login;
      return token;
    },
    async session({ session, token }) {
      if (session?.user) session.user.login = token.login;
      return session;
    }
  }
});
