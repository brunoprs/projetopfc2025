import React, { useState, useEffect } from "react";
import { socialMediaService } from "../../services/api";

export default function AdminSocials() {
  const [socials, setSocials] = useState([]);
  const [form, setForm] = useState({ platform: "", url: "" });

  const loadSocials = async () => {
    try {
      const data = await socialMediaService.getAll();
      setSocials(data.social_media || []);
    } catch (err) {
      alert("Erro ao carregar redes sociais: " + err.message);
    }
  };

  useEffect(() => {
    loadSocials();
  }, []);

  const handleCreate = async (e) => {
    e.preventDefault();
    try {
      await socialMediaService.create(form.platform, form.url);
      alert("Rede adicionada com sucesso!");
      setForm({ platform: "", url: "" });
      loadSocials();
    } catch (err) {
      alert("Erro: " + err.message);
    }
  };

  return (
    <div className="p-6">
      <h2>🌐 Gerenciar Redes Sociais</h2>

      <form onSubmit={handleCreate}>
        <input placeholder="Plataforma" value={form.platform} onChange={(e) => setForm({ ...form, platform: e.target.value })} />
        <input placeholder="URL" value={form.url} onChange={(e) => setForm({ ...form, url: e.target.value })} />
        <button type="submit">Criar Rede</button>
      </form>

      <h3>Lista de Redes</h3>
      <ul>
        {socials.map((s) => (
          <li key={s.id}>
            {s.platform} — {s.url}
          </li>
        ))}
      </ul>
    </div>
  );
}
