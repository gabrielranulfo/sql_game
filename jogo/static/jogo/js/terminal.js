/* Terminal SQL do Caso Ambar */
(function () {
  const raiz = document.getElementById('terminal');
  if (!raiz) return;

  const entrada = document.getElementById('sql');
  const btnExec = document.getElementById('sql-executar');
  const btnFechar = document.getElementById('terminal-fechar');
  const elErro = document.getElementById('sql-erro');
  const elInfo = document.getElementById('sql-info');
  const elRes = document.getElementById('sql-resultados');
  const elPistas = document.getElementById('lista-pistas');
  const elEsquema = document.getElementById('esquema');
  const elHist = document.getElementById('historico');
  const aviso = document.getElementById('aviso');

  window.aviso = function (texto, ok) {
    aviso.textContent = texto;
    aviso.className = ok ? 'aviso-visivel aviso-ok' : 'aviso-visivel';
    clearTimeout(window._avisoT);
    window._avisoT = setTimeout(function () {
      aviso.className = 'aviso-oculto';
    }, 5200);
  };

  function esconder(el, classe) {
    el.className = classe;
  }

  window.abrirTerminal = function () {
    raiz.classList.remove('terminal-oculto');
    raiz.classList.add('terminal-visivel');
    raiz.setAttribute('aria-hidden', 'false');
    atualizarPistas();
    entrada.focus();
  };

  function fecharTerminal() {
    raiz.classList.remove('terminal-visivel');
    raiz.classList.add('terminal-oculto');
    raiz.setAttribute('aria-hidden', 'true');
  }

  document.addEventListener('click', function (ev) {
    if (ev.target.closest('[data-abrir-terminal]')) {
      ev.preventDefault();
      window.abrirTerminal();
    }
  });
  btnFechar.addEventListener('click', fecharTerminal);
  document.addEventListener('keydown', function (ev) {
    if (ev.key === 'Escape' && raiz.classList.contains('terminal-visivel')) fecharTerminal();
  });
  raiz.addEventListener('click', function (ev) {
    if (ev.target === raiz) fecharTerminal();
  });

  function esc(s) {
    return String(s == null ? '' : s)
      .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;');
  }

  function desenharEsquema() {
    if (!JOGO.schema) return;
    let html = '';
    Object.keys(JOGO.schema).forEach(function (tabela) {
      html += '<button type="button" class="esquema-tabela" data-tabela="' + esc(tabela) + '">' +
        esc(tabela) + '</button>' +
        '<div class="esquema-colunas">' + esc(JOGO.schema[tabela]) + '</div>';
    });
    elEsquema.innerHTML = html;
  }

  elEsquema.addEventListener('click', function (ev) {
    const btn = ev.target.closest('[data-tabela]');
    if (!btn) return;
    entrada.value = 'SELECT * FROM ' + btn.getAttribute('data-tabela') + ' LIMIT 20;';
    entrada.focus();
  });

  function desenharTabela(dados) {
    if (!dados.colunas.length) {
      elRes.innerHTML = '<p class="sem-resultado">Consulta executada sem retorno de linhas.</p>';
      return;
    }
    let html = '<div class="rolagem"><table><thead><tr>';
    dados.colunas.forEach(function (c) { html += '<th>' + esc(c) + '</th>'; });
    html += '</tr></thead><tbody>';
    dados.linhas.forEach(function (linha) {
      html += '<tr>';
      linha.forEach(function (v) {
        html += '<td>' + (v === null ? '<em>NULL</em>' : esc(v)) + '</td>';
      });
      html += '</tr>';
    });
    html += '</tbody></table></div>';
    elRes.innerHTML = html;
  }

  function executar() {
    const sql = entrada.value.trim();
    if (!sql) return;
    esconder(elErro, 'erro-oculto');
    esconder(elInfo, 'info-oculto');
    elRes.innerHTML = '<p class="sem-resultado">Consultando a base do inquérito…</p>';

    fetch(JOGO.urlQuery, {
      method: 'POST',
      headers: {'Content-Type': 'application/json', 'X-CSRFToken': JOGO.csrf},
      body: JSON.stringify({sql: sql})
    })
      .then(function (r) { return r.json(); })
      .then(function (d) {
        if (!d.ok) {
          elRes.innerHTML = '';
          elErro.textContent = d.error;
          esconder(elErro, 'erro-visivel');
          return;
        }
        desenharTabela(d);
        let info = d.total + ' linha(s) · ' + d.tempo_ms + ' ms';
        if (d.truncado) info += ' · mostrando apenas as primeiras 100 linhas';
        elInfo.textContent = info;
        esconder(elInfo, 'info-visivel');

        if (d.novas_pistas && d.novas_pistas.length) {
          d.novas_pistas.forEach(function (p) {
            window.aviso('PISTA ' + p.n + ' DESBLOQUEADA — ' + p.titulo + ': ' + p.narrativa, true);
          });
        }
        atualizarBarra(d.progresso, d.descobertas.length);
        atualizarPistas();
        if (d.finalizou) {
          window.aviso('Todas as pistas apuradas. Registre a acusação na porta da sala.', true);
        }
      })
      .catch(function () {
        elErro.textContent = 'Falha de conexao com o servidor.';
        esconder(elErro, 'erro-visivel');
      });
  }

  btnExec.addEventListener('click', executar);
  entrada.addEventListener('keydown', function (ev) {
    if ((ev.ctrlKey || ev.metaKey) && ev.key === 'Enter') {
      ev.preventDefault();
      executar();
    }
  });

  function atualizarBarra(progresso, total) {
    const barra = document.querySelector('.progresso .barra span');
    const rotulo = document.querySelector('.progresso small');
    if (barra) barra.style.width = (progresso || 0) + '%';
    if (rotulo) rotulo.textContent = (total || 0) + '/6 pistas';
  }

  function atualizarPistas() {
    fetch(JOGO.urlPistas, {headers: {'Accept': 'application/json'}})
      .then(function (r) { return r.json(); })
      .then(function (d) {
        let html = '';
        d.detalhes.forEach(function (p) {
          html += '<li class="' + (p.liberada ? 'pista-liberada' : 'pista-trancada') + '">' +
            '<strong>' + p.n + '. ' + esc(p.titulo) + '</strong>' +
            (p.liberada ? '<p>' + esc(p.narrativa) + '</p>' : '<p>— trancada —</p>') +
            '</li>';
        });
        elPistas.innerHTML = html;
        atualizarBarra(d.progresso, d.descobertas.length);

        let h = '';
        d.historico.forEach(function (q) {
          h += '<li><button type="button" class="hist-sql">' + esc(q) + '</button></li>';
        });
        elHist.innerHTML = h || '<li class="sem-resultado">Nenhuma consulta ainda.</li>';
      });
  }

  elHist.addEventListener('click', function (ev) {
    const btn = ev.target.closest('.hist-sql');
    if (!btn) return;
    entrada.value = btn.textContent;
    executar();
  });

  desenharEsquema();
  atualizarPistas();
})();
