#!/usr/bin/env python3
"""
Generador de Corpus Multilenguaje
Extrae: commits, issues
"""

import os
import json
from github import Github
from pathlib import Path

# Configuración: Ingreso de GITHUB TOKEN
TOKEN = os.getenv('GITHUB_TOKEN', '')
g = Github(TOKEN)

# Directorios
BASE_DIR = Path("corpus_multilenguaje")
CORPUS_DIR = BASE_DIR / "corpus_generado"

# Crear directorios
BASE_DIR.mkdir(exist_ok=True)
CORPUS_DIR.mkdir(exist_ok=True)

def extraer_readme(repo):
    """Extrae contenido del README usando API"""
    try:
        readme = repo.get_readme()
        return readme.decoded_content.decode('utf-8')
    except:
        return None

def extraer_commits(repo_full_name, limite=100):
    """Extrae mensajes de commits usando API"""
    try:
        repo = g.get_repo(repo_full_name)
        commits = repo.get_commits()[:limite]
        
        commits_extraidos = []
        for commit in commits:
            try:
                commits_extraidos.append({
                    'sha': commit.sha,
                    'mensaje': commit.commit.message,
                    'autor': commit.commit.author.name if commit.commit.author else 'Unknown',
                    'fecha': str(commit.commit.author.date) if commit.commit.author else None
                })
            except:
                pass
        
        return commits_extraidos
    except Exception as e:
        print(f"   ⚠️  Error extrayendo commits: {e}")
        return []

def extraer_issues(repo_full_name, limite=50):
    """Extrae issues usando API"""
    try:
        repo = g.get_repo(repo_full_name)
        issues = repo.get_issues(state='all')[:limite]
        
        issues_extraidos = []
        for issue in issues:
            try:
                # Extraer comentarios del issue
                comentarios = []
                for comment in issue.get_comments()[:10]:
                    comentarios.append({
                        'autor': comment.user.login if comment.user else 'Unknown',
                        'body': comment.body,
                        'fecha': str(comment.created_at)
                    })
                
                issues_extraidos.append({
                    'numero': issue.number,
                    'titulo': issue.title,
                    'body': issue.body,
                    'estado': issue.state,
                    'comentarios': comentarios,
                    'labels': [label.name for label in issue.labels]
                })
            except:
                pass
        
        return issues_extraidos
    except Exception as e:
        print(f"   ⚠️  Error extrayendo issues: {e}")
        return []

def extraer_pull_requests(repo_full_name, limite=30):
    """Extrae pull requests usando API"""
    try:
        repo = g.get_repo(repo_full_name)
        prs = repo.get_pulls(state='all')[:limite]
        
        prs_extraidos = []
        for pr in prs:
            try:
                # Extraer comentarios del PR
                comentarios = []
                for comment in pr.get_comments()[:10]:
                    comentarios.append({
                        'autor': comment.user.login if comment.user else 'Unknown',
                        'body': comment.body,
                        'fecha': str(comment.created_at)
                    })
                
                prs_extraidos.append({
                    'numero': pr.number,
                    'titulo': pr.title,
                    'body': pr.body,
                    'estado': pr.state,
                    'comentarios': comentarios
                })
            except:
                pass
        
        return prs_extraidos
    except Exception as e:
        print(f"   ⚠️  Error extrayendo PRs: {e}")
        return []

def procesar_repositorio(repo_info):
    """Procesa un repositorio y extrae contenido vía API"""
    repo_name = repo_info['full_name']
    print(f"\n📦 Procesando: {repo_name}")
    
    corpus_repo = {
        'metadata': {
            'full_name': repo_name,
            'url': repo_info['url'],
            'pais': repo_info['pais'],
            'estrellas': repo_info['estrellas'],
            'commits': repo_info['commits'],
            'lenguaje': repo_info['lenguaje']
        },
        'contenido': {}
    }
    
    # 1. Extraer README vía API
    print(f"   📄 Extrayendo README...")
    try:
        repo = g.get_repo(repo_name)
        readme = extraer_readme(repo)
        if readme:
            corpus_repo['contenido']['readme'] = readme
            print(f"      ✅ README extraído ({len(readme)} caracteres)")
    except Exception as e:
        print(f"      ⚠️  No se encontró README")
    
    # 2. Extraer commits
    print(f"   📝 Extrayendo commits...")
    commits = extraer_commits(repo_name, limite=100)
    if commits:
        corpus_repo['contenido']['commits'] = commits
        print(f"      ✅ {len(commits)} commits extraídos")
    
    # 3. Extraer issues
    print(f"   🐛 Extrayendo issues...")
    issues = extraer_issues(repo_name, limite=50)
    if issues:
        corpus_repo['contenido']['issues'] = issues
        print(f"      ✅ {len(issues)} issues extraídos")
    
    # 4. Extraer PRs
    print(f"   🔀 Extrayendo pull requests...")
    prs = extraer_pull_requests(repo_name, limite=30)
    if prs:
        corpus_repo['contenido']['pull_requests'] = prs
        print(f"      ✅ {len(prs)} PRs extraídos")
    
    return corpus_repo

def generar_corpus_completo(json_file):
    """Genera el corpus completo desde el JSON de repositorios"""
    
    print("="*80)
    print("  GENERADOR DE CORPUS MULTILENGUAJE - SOLO API")
    print("="*80)
    print(f"📂 Corpus generado: {CORPUS_DIR}")
    print("="*80)
    
    # Leer JSON con repositorios
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Combinar repositorios de ambos países
    repos_mexico = data.get('mexico', [])
    repos_argentina = data.get('argentina', [])
    repos_ecuador= data.get('ecuador', [])
    repos_colombia = data.get('colombia', [])
    
    todos_repos = repos_mexico + repos_argentina + repos_ecuador + repos_colombia
    
    print(f"\n📊 Total de repositorios a procesar: {len(todos_repos)}")
    print(f"   🇲🇽 México: {len(repos_mexico)}")
    print(f"   🇦🇷 Argentina: {len(repos_argentina)}")
    print(f"   🇪🇨 Ecuador: {len(repos_ecuador)}")
    print(f"   🇨🇴 Colombia: {len(repos_colombia)}")
    
    corpus_completo = []
    
    # Procesar cada repositorio
    for idx, repo in enumerate(todos_repos, 1):
        print(f"\n[{idx}/{len(todos_repos)}]", end=" ")
        
        try:
            corpus_repo = procesar_repositorio(repo)
            corpus_completo.append(corpus_repo)
            
            # Guardar progreso cada 5 repos
            if idx % 5 == 0:
                temp_file = CORPUS_DIR / f'corpus_progreso_{idx}.json'
                with open(temp_file, 'w', encoding='utf-8') as f:
                    json.dump(corpus_completo, f, indent=2, ensure_ascii=False)
                print(f"\n   💾 Progreso guardado")
        
        except Exception as e:
            print(f"   ❌ Error: {e}")
            continue
    
    # Guardar corpus final
    corpus_final_file = CORPUS_DIR / 'corpus_multilenguaje_completo.json'
    with open(corpus_final_file, 'w', encoding='utf-8') as f:
        json.dump(corpus_completo, f, indent=2, ensure_ascii=False)
    
    # Generar estadísticas
    print("\n" + "="*80)
    print("  ESTADÍSTICAS DEL CORPUS GENERADO")
    print("="*80)
    
    total_repos = len(corpus_completo)
    total_readmes = sum(1 for c in corpus_completo if 'readme' in c['contenido'])
    total_commits = sum(len(c['contenido'].get('commits', [])) for c in corpus_completo)
    total_issues = sum(len(c['contenido'].get('issues', [])) for c in corpus_completo)
    total_prs = sum(len(c['contenido'].get('pull_requests', [])) for c in corpus_completo)
    
    print(f"\n📊 Repositorios procesados: {total_repos}")
    print(f"📄 READMEs extraídos: {total_readmes}")
    print(f"📝 Commits: {total_commits}")
    print(f"🐛 Issues: {total_issues}")
    print(f"🔀 Pull Requests: {total_prs}")
    
    print(f"\n✅ Corpus guardado en: {corpus_final_file}")
    print(f"📁 Tamaño: {corpus_final_file.stat().st_size / (1024*1024):.2f} MB")
    
    return corpus_completo

# Ejecutar
if __name__ == "__main__":
    JSON_FILE = 'top30_desde_2020.json'
    
    if not os.path.exists(JSON_FILE):
        print(f"❌ Archivo no encontrado: {JSON_FILE}")
    else:
        import os
        corpus = generar_corpus_completo(JSON_FILE)
        print("\n🎉 ¡Corpus generado!")