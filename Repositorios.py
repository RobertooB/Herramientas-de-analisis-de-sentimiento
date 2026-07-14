#!/usr/bin/env python3
"""
Buscar repositorios de 4 países
"""

from github import Github
from github.GithubException import RateLimitExceededException
import json
from datetime import datetime, timezone
import time
import os

# Configuración: Ingreso de GITHUB TOKEN
TOKEN = os.getenv('GITHUB_TOKEN', '')
g = Github(TOKEN)

def buscar_top_repos_por_commits(pais, top_n=30, max_usuarios=50):
    """Busca los top N repositorios con más commits de un país (desde 2020)"""
    
    print(f"\n🔍 Buscando top {top_n} repositorios de {pais} (desde 2020)...")
    
    query = f"location:{pais} repos:>5"
    usuarios = g.search_users(query=query, sort="repositories", order="desc")
    
    repos_con_commits = []
    fecha_limite = datetime(2020, 1, 1, tzinfo=timezone.utc)
    usuarios_procesados = 0
    
    try:
        for idx, usuario in enumerate(usuarios[:max_usuarios]):
            try:
                print(f"[{idx+1}/{max_usuarios}] Usuario: {usuario.login}", end=" ")
                usuarios_procesados += 1
                
                repos_del_usuario = 0
                for repo in usuario.get_repos()[:5]:
                    try:
                        if repo.private:
                            continue
                        
                        # Verificar fecha de creación
                        if repo.created_at < fecha_limite:
                            continue
                        
                        # Contar commits
                        commits_count = repo.get_commits().totalCount
                        
                        if commits_count < 50:
                            continue
                        
                        repo_info = {
                            "pais": pais,
                            "usuario": usuario.login,
                            "nombre": repo.name,
                            "full_name": repo.full_name,
                            "url": repo.html_url,
                            "descripcion": repo.description,
                            "estrellas": repo.stargazers_count,
                            "forks": repo.forks_count,
                            "commits": commits_count,
                            "lenguaje": repo.language,
                            "creado": str(repo.created_at),
                            "actualizado": str(repo.updated_at)
                        }
                        
                        repos_con_commits.append(repo_info)
                        repos_del_usuario += 1
                        
                    except RateLimitExceededException:
                        print(f"⚠️ Límite de API alcanzado. Esperando 60 segundos...")
                        time.sleep(60)
                        continue
                    except Exception as e:
                        continue
                
                print(f"✅ {repos_del_usuario} repos encontrados")
                
                # Si ya tenemos suficientes, podemos parar
                if len(repos_con_commits) >= top_n * 2:
                    print(f"✅ Objetivo alcanzado ({len(repos_con_commits)} repos)")
                    break
                    
            except RateLimitExceededException:
                print(f"⚠️ Límite de API alcanzado. Esperando 60 segundos...")
                time.sleep(60)
                continue
            except Exception as e:
                print(f"⚠️ Error con usuario: {e}")
                continue
        
        print(f"✅ Procesados {usuarios_procesados} usuarios de {pais}")
        
    except RateLimitExceededException:
        print(f"❌ Límite de API excedido. Intenta más tarde.")
        return []
    
    # Ordenar por commits y tomar top N
    repos_ordenados = sorted(repos_con_commits, key=lambda x: x['commits'], reverse=True)
    return repos_ordenados[:top_n]

def mostrar_top_pais(pais, repos):
    """Muestra los resultados de un país"""
    print("\n" + "="*80)
    print(f"  TOP 30 {pais.upper()} - REPOSITORIOS CON MÁS COMMITS (DESDE 2020)")
    print("="*80 + "\n")
    
    if not repos:
        print(f"⚠️ No se encontraron repositorios para {pais}\n")
        return
    
    for idx, repo in enumerate(repos, 1):
        año_creacion = repo['creado'][:4]
        print(f"{idx:2d}. {repo['full_name']} ({año_creacion})")
        print(f"    📊 {repo['commits']:,} commits | ⭐ {repo['estrellas']} | 🍴 {repo['forks']} | 💻 {repo['lenguaje']}")
        print(f"    🔗 {repo['url']}")
        print()

# Buscar top 30 de cada país
print("="*80)
print("  BUSCANDO TOP 30 CON MÁS COMMITS POR PAÍS (DESDE 2020)")
print("="*80)

paises = ["Mexico", "Argentina", "Ecuador", "Colombia"]
resultados = {"criterio": "Repositorios creados desde 2020"}
total_repos = 0

for pais in paises:
    top_30 = buscar_top_repos_por_commits(pais, top_n=30, max_usuarios=50)
    resultados[pais.lower()] = top_30
    total_repos += len(top_30)
    
    # Mostrar resultados
    mostrar_top_pais(pais, top_30)
    
    # Pequeña pausa entre países para no saturar API
    time.sleep(5)

# Agregar total
resultados["total"] = total_repos

# Guardar
with open('top30_desde_2020.json', 'w', encoding='utf-8') as f:
    json.dump(resultados, f, indent=2, ensure_ascii=False)

# Resumen final
print("="*80)
print(f"✅ México: {len(resultados.get('mexico', []))} repositorios")
print(f"✅ Argentina: {len(resultados.get('argentina', []))} repositorios")
print(f"✅ Ecuador: {len(resultados.get('ecuador', []))} repositorios")
print(f"✅ Colombia: {len(resultados.get('colombia', []))} repositorios")
print(f"💾 Total: {resultados['total']} repositorios")
print(f"💾 Guardado en: top30_desde_2020.json")
print("="*80)