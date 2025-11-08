import React, { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Separator } from "@/components/ui/separator";
import { useNavigate } from "react-router-dom";
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
  AlertDialogTrigger,
} from "@/components/ui/alert-dialog";
import api from "@/services/api";

const MyAccount = () => {
  const [user, setUser] = useState(null);
  const [formData, setFormData] = useState({ username: "", name: "", email: "" });
  const [message, setMessage] = useState("");
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const [showPasswordForm, setShowPasswordForm] = useState(false);
  const [passwordForm, setPasswordForm] = useState({ currentPassword: "", newPassword: "", confirmPassword: "" });
  const [passwordLoading, setPasswordLoading] = useState(false);
  const [passwordMessage, setPasswordMessage] = useState("");

  const [deleteLoading, setDeleteLoading] = useState(false);

  useEffect(() => {
    const token = localStorage.getItem("token");
    if (!token) {
      navigate("/login");
      return;
    }

    const fetchUser = async () => {
      try {
        const data = await api.authService.getCurrentUser();
        setUser(data);
        setFormData({
          username: data.username,
          name: data.name,
          email: data.email,
        });
      } catch (err) {
        console.error("Erro ao carregar dados do usuário:", err);
        localStorage.removeItem("token");
        localStorage.removeItem("user");
        navigate("/login");
      }
    };
    fetchUser();
  }, [navigate]);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData({ ...formData, [name]: value });
  };

  const handlePasswordChange = (e) => {
    const { name, value } = e.target;
    setPasswordForm({ ...passwordForm, [name]: value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setMessage("");
    setLoading(true);

    try {
      const data = await api.userService.updateSelf(formData);

      setUser({ ...user, ...formData });
      localStorage.setItem("user", JSON.stringify({ ...user, ...formData }));

      setMessage("✅ Dados atualizados com sucesso!");
    } catch (error) {
      console.error("Erro ao atualizar usuário:", error);
      setMessage("❌ " + (error.message || "Erro ao atualizar usuário."));
    } finally {
      setLoading(false);
    }
  };

  const handleSubmitPassword = async (e) => {
    e.preventDefault();
    setPasswordMessage("");

    if (passwordForm.newPassword !== passwordForm.confirmPassword) {
      setPasswordMessage("❌ As novas senhas não coincidem.");
      return;
    }
    if (passwordForm.newPassword.length < 6) {
      setPasswordMessage("❌ A nova senha deve ter pelo menos 6 caracteres.");
      return;
    }

    setPasswordLoading(true);

    const payload = {
      current_password: passwordForm.currentPassword,
      new_password: passwordForm.newPassword
    };

    try {
      const data = await api.userService.changePassword(payload);
      setPasswordMessage(`✅ ${data.message
        }`);
      setPasswordForm({ currentPassword: "", newPassword: "", confirmPassword: "" });
      setShowPasswordForm(false);
    } catch (error) {
      setPasswordMessage("❌ " + (error.message || "Erro ao alterar senha."));
    } finally {
      setPasswordLoading(false);
    }
  };

  const handleDeleteAccount = async () => {
    setDeleteLoading(true);

    try {
      await api.userService.deleteAccount();

      localStorage.removeItem("token");
      localStorage.removeItem("user");
      navigate('/');
    } catch (error) {
      alert("Erro ao excluir conta: " + error.message);
      setDeleteLoading(false);
    }
  };

  if (!user) return <p className="text-center mt-10">Carregando...</p>;

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 px-4 py-10">
      <div className="w-full max-w-md bg-white shadow-lg rounded-2xl p-8 border border-gray-100">

        <div className="flex flex-col items-center mb-6">
          <div className="bg-secondary text-primary font-bold text-xl w-16 h-16 rounded-full flex items-center justify-center mb-2">
            {user?.name?.[0]?.toUpperCase()}
          </div>
          <h1 className="text-2xl font-bold text-primary">Minha Conta</h1>
        </div>

        <form onSubmit={handleSubmit} className="space-y-5">
          <div className="space-y-2">
            <Label htmlFor="username">Nome de Usuário</Label>
            <Input
              id="username"
              type="text"
              name="username"
              value={formData.username}
              onChange={handleChange}
            />
          </div>
          <div className="space-y-2">
            <Label htmlFor="name">Nome Completo</Label>
            <Input
              id="name"
              type="text"
              name="name"
              value={formData.name}
              onChange={handleChange}
            />
          </div>
          <div className="space-y-2">
            <Label htmlFor="email">E-mail</Label>
            <Input
              id="email"
              type="email"
              name="email"
              value={formData.email}
              disabled
              className="cursor-not-allowed bg-gray-100"
            />
            <p className="text-xs text-gray-400 mt-1">
              O e-mail não pode ser alterado.
            </p>
          </div>

          {!showPasswordForm && (
            <Button
              type="button"
              className="w-full"
              variant="outline"
              onClick={() => setShowPasswordForm(true)}
            >
              Alterar Senha
            </Button>
          )}

          <Button type="submit" className="w-full" disabled={loading}>
            {loading ? "Salvando..." : "Salvar Alterações de Perfil"}
          </Button>

          {message && (
            <p className="text-center text-sm mt-3">{message}</p>
          )}
        </form>

        {showPasswordForm && (
          <>
            <Separator className="my-8" />
            <div className="space-y-5">
              <div className="flex justify-between items-center">
                <h2 className="text-xl font-bold text-primary">Alterar Senha</h2>
                <Button variant="ghost" size="sm" onClick={() => setShowPasswordForm(false)}>
                  Cancelar
                </Button>
              </div>
              <form onSubmit={handleSubmitPassword} className="space-y-5">
                <div className="space-y-2">
                  <Label htmlFor="currentPassword">Senha Atual</Label>
                  <Input
                    id="currentPassword"
                    type="password"
                    name="currentPassword"
                    value={passwordForm.currentPassword}
                    onChange={handlePasswordChange}
                    required
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="newPassword">Nova Senha</Label>
                  <Input
                    id="newPassword"
                    type="password"
                    name="newPassword"
                    value={passwordForm.newPassword}
                    onChange={handlePasswordChange}
                    required
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="confirmPassword">Confirmar Nova Senha</Label>
                  <Input
                    id="confirmPassword"
                    type="password"
                    name="confirmPassword"
                    value={passwordForm.confirmPassword}
                    onChange={handlePasswordChange}
                    required
                  />
                </div>
                <Button type="submit" className="w-full" variant="secondary" disabled={passwordLoading}>
                  {passwordLoading ? "Alterando..." : "Confirmar Nova Senha"}
                </Button>
                {passwordMessage && (
                  <p className="text-center text-sm mt-3">{passwordMessage}</p>
                )}
              </form>
            </div>
          </>
        )}

        <Separator className="my-8" />

        <div className="space-y-4">
          <h2 className="text-xl font-bold text-destructive">Excluir Conta</h2>
          <p className="text-sm text-muted-foreground">
            A exclusão da sua conta é permanente e não pode ser revertida.
          </p>

          <AlertDialog>
            <AlertDialogTrigger asChild>
              <Button variant="destructive" className="w-full">
                Excluir minha conta
              </Button>
            </AlertDialogTrigger>
            <AlertDialogContent>
              <AlertDialogHeader>
                <AlertDialogTitle>Você tem certeza absoluta?</AlertDialogTitle>
                <AlertDialogDescription>
                  Esta ação é irreversível. Todos os seus dados, favoritos e
                  comentários serão permanentemente excluídos.
                </AlertDialogDescription>
              </AlertDialogHeader>
              <AlertDialogFooter>
                <AlertDialogCancel>Cancelar</AlertDialogCancel>
                <AlertDialogAction
                  onClick={handleDeleteAccount}
                  disabled={deleteLoading}
                  className="bg-destructive hover:bg-destructive/90"
                >
                  {deleteLoading ? "Excluindo..." : "Sim, excluir conta"}
                </AlertDialogAction>
              </AlertDialogFooter>
            </AlertDialogContent>
          </AlertDialog>

        </div>
      </div>
    </div>
  );
};

export default MyAccount;