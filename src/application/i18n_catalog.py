"""Stable message codes for gettext. msgid = code; msgstr = localized text."""
from __future__ import annotations

MESSAGES: dict[str, dict[str, str]] = {
  'action.add': {
    "en_US": '➕ Add',
    "pt_BR": '➕ Adicionar',
  },
  'action.delete': {
    "en_US": '🗑️ Delete',
    "pt_BR": '🗑️ Excluir',
  },
  'action.duplicate': {
    "en_US": '📑 Duplicate',
    "pt_BR": '📑 Duplicar',
  },
  'action.edit': {
    "en_US": '✏️ Edit',
    "pt_BR": '✏️ Editar',
  },
  'action.export': {
    "en_US": '💾 Export',
    "pt_BR": '💾 Exportar',
  },
  'action.import': {
    "en_US": '📥 Import',
    "pt_BR": '📥 Importar',
  },
  'action.run': {
    "en_US": '➕ Run',
    "pt_BR": '➕ Executar',
  },
  'action.update': {
    "en_US": '🔄 Update',
    "pt_BR": '🔄 Atualizar',
  },
  'action.view_results': {
    "en_US": '📊 View Results',
    "pt_BR": '📊 Ver resultados',
  },
  'analysis.col.name': {
    "en_US": 'Analysis Name',
    "pt_BR": 'Nome',
  },
  'analysis.col.output_kind': {
    "en_US": 'Output Kind',
    "pt_BR": 'Tipo de saída',
  },
  'analysis.err.native_cannot_delete': {
    "en_US": 'Native analyses cannot be deleted.',
    "pt_BR": 'Análises nativas não podem ser removidas.',
  },
  'analysis.msg.delete_confirm': {
    "en_US": 'Delete {label} permanently?{extra}',
    "pt_BR": 'Excluir {label} permanentemente?{extra}',
  },
  'analysis.msg.delete_partial': {
    "en_US": 'Some analyses could not be deleted:\n\n',
    "pt_BR": 'Algumas análises não puderam ser excluídas:\n\n',
  },
  'analysis.msg.n_analyses': {
    "en_US": '{n} analyses',
    "pt_BR": '{n} análises',
  },
  'analysis.msg.select_delete': {
    "en_US": 'Please select at least one analysis to delete.',
    "pt_BR": 'Selecione pelo menos uma análise para excluir.',
  },
  'analysis.msg.skip_native': {
    "en_US": '({n} native analysis(es) will be skipped.)',
    "pt_BR": '({n} análise(s) nativa(s) serão ignoradas.)',
  },
  'analysis.view.title': {
    "en_US": 'Analyses Library',
    "pt_BR": 'Biblioteca de Análises',
  },
  'app.brand': {
    "en_US": 'ML STUDIO',
    "pt_BR": 'ML STUDIO',
  },
  'app.title': {
    "en_US": 'ML Viewer',
    "pt_BR": 'ML Viewer',
  },
  'common.browse': {
    "en_US": 'Browse',
    "pt_BR": 'Procurar',
  },
  'common.cancel': {
    "en_US": 'Cancel',
    "pt_BR": 'Cancelar',
  },
  'common.close': {
    "en_US": 'Close',
    "pt_BR": 'Fechar',
  },
  'common.confirm': {
    "en_US": 'Confirm',
    "pt_BR": 'Confirmar',
  },
  'common.confirm_delete': {
    "en_US": 'Confirm Delete',
    "pt_BR": 'Confirmar exclusão',
  },
  'common.custom': {
    "en_US": 'Custom',
    "pt_BR": 'Personalizado',
  },
  'common.delete': {
    "en_US": 'Delete',
    "pt_BR": 'Excluir',
  },
  'common.delete_error': {
    "en_US": 'Delete Error',
    "pt_BR": 'Erro ao excluir',
  },
  'common.description': {
    "en_US": 'Description',
    "pt_BR": 'Descrição',
  },
  'common.edit': {
    "en_US": 'Edit',
    "pt_BR": 'Editar',
  },
  'common.error': {
    "en_US": 'Error',
    "pt_BR": 'Erro',
  },
  'common.error_loading': {
    "en_US": 'Error loading',
    "pt_BR": 'Erro ao carregar',
  },
  'common.export': {
    "en_US": 'Export',
    "pt_BR": 'Exportar',
  },
  'common.export_error': {
    "en_US": 'Export Error',
    "pt_BR": 'Erro de exportação',
  },
  'common.file': {
    "en_US": 'File',
    "pt_BR": 'Arquivo',
  },
  'common.filetypes.csv': {
    "en_US": 'CSV Files',
    "pt_BR": 'Arquivos CSV',
  },
  'common.filetypes.csv_long': {
    "en_US": 'Comma separated values files',
    "pt_BR": 'Arquivos CSV',
  },
  'common.filetypes.python': {
    "en_US": 'Python Files',
    "pt_BR": 'Arquivos Python',
  },
  'common.filetypes.zip': {
    "en_US": 'ZIP Archive',
    "pt_BR": 'Arquivo ZIP',
  },
  'common.id': {
    "en_US": 'ID',
    "pt_BR": 'ID',
  },
  'common.import': {
    "en_US": 'Import',
    "pt_BR": 'Importar',
  },
  'common.import_error': {
    "en_US": 'Import Error',
    "pt_BR": 'Erro de importação',
  },
  'common.logs': {
    "en_US": 'Logs',
    "pt_BR": 'Logs',
  },
  'common.metric': {
    "en_US": 'Metric',
    "pt_BR": 'Métrica',
  },
  'common.metrics': {
    "en_US": 'Metrics',
    "pt_BR": 'Métricas',
  },
  'common.name': {
    "en_US": 'Name',
    "pt_BR": 'Nome',
  },
  'common.native': {
    "en_US": 'Native',
    "pt_BR": 'Nativo',
  },
  'common.no_description': {
    "en_US": '(No description)',
    "pt_BR": '(Sem descrição)',
  },
  'common.no_description_available': {
    "en_US": 'No description available.',
    "pt_BR": 'Nenhuma descrição disponível.',
  },
  'common.no_file_selected': {
    "en_US": 'No file selected',
    "pt_BR": 'Nenhum arquivo selecionado',
  },
  'common.output_results': {
    "en_US": 'Output / Results',
    "pt_BR": 'Saída / Resultados',
  },
  'common.select_csv': {
    "en_US": 'Select CSV',
    "pt_BR": 'Selecionar CSV',
  },
  'common.select_file': {
    "en_US": 'Select a File',
    "pt_BR": 'Selecionar um arquivo',
  },
  'common.source': {
    "en_US": 'Source',
    "pt_BR": 'Origem',
  },
  'common.status': {
    "en_US": 'Status',
    "pt_BR": 'Status',
  },
  'common.success': {
    "en_US": 'Success',
    "pt_BR": 'Sucesso',
  },
  'common.type': {
    "en_US": 'Type',
    "pt_BR": 'Tipo',
  },
  'common.update': {
    "en_US": 'Update',
    "pt_BR": 'Atualizar',
  },
  'common.update_error': {
    "en_US": 'Update Error',
    "pt_BR": 'Erro de atualização',
  },
  'common.validation_error': {
    "en_US": 'Validation Error',
    "pt_BR": 'Erro de validação',
  },
  'common.value': {
    "en_US": 'Value',
    "pt_BR": 'Valor',
  },
  'common.warning': {
    "en_US": 'Warning',
    "pt_BR": 'Aviso',
  },
  'dataset.col.added_on': {
    "en_US": 'Added On',
    "pt_BR": 'Adicionado em',
  },
  'dataset.col.file_path': {
    "en_US": 'File Path',
    "pt_BR": 'Caminho do arquivo',
  },
  'dataset.col.target': {
    "en_US": 'Target',
    "pt_BR": 'Alvo',
  },
  'dataset.err.integrity': {
    "en_US": "Dataset '{name}' is corrupted or was modified externally (MD5 mismatch).",
    "pt_BR": "Dataset '{name}' está corrompido ou foi alterado externamente (MD5 não corresponde).",
  },
  'dataset.err.not_found': {
    "en_US": 'Dataset with ID {id} was not found.',
    "pt_BR": 'Dataset com ID {id} não encontrado.',
  },
  'dataset.err.supervised_requires_target': {
    "en_US": 'Supervised datasets require a valid target column.',
    "pt_BR": 'Datasets supervisionados exigem uma coluna alvo válida.',
  },
  'dataset.err.unsupervised_no_target': {
    "en_US": 'Unsupervised datasets do not use a target; leave it empty.',
    "pt_BR": 'Datasets não supervisionados não usam alvo; deixe vazio.',
  },
  'dataset.err.unsupported_problem_type': {
    "en_US": 'Unsupported problem type: {problem_type}',
    "pt_BR": 'Tipo de problema não suportado: {problem_type}',
  },
  'dataset.form.add_title': {
    "en_US": 'Add New Dataset',
    "pt_BR": 'Adicionar Dataset',
  },
  'dataset.form.edit_title': {
    "en_US": 'Edit Dataset',
    "pt_BR": 'Editar Dataset',
  },
  'dataset.form.err_name_file': {
    "en_US": 'Name and File are required.',
    "pt_BR": 'Nome e arquivo são obrigatórios.',
  },
  'dataset.form.err_target_required': {
    "en_US": 'Target Variable is required for supervised datasets.',
    "pt_BR": 'A variável alvo é obrigatória para datasets supervisionados.',
  },
  'dataset.form.file': {
    "en_US": 'File (CSV):',
    "pt_BR": 'Arquivo (CSV):',
  },
  'dataset.form.name': {
    "en_US": 'Dataset Name:',
    "pt_BR": 'Nome do Dataset:',
  },
  'dataset.form.paradigm_type': {
    "en_US": 'Paradigm & Problem Type:',
    "pt_BR": 'Paradigma e tipo de problema:',
  },
  'dataset.form.save': {
    "en_US": 'Save Dataset',
    "pt_BR": 'Salvar Dataset',
  },
  'dataset.form.target': {
    "en_US": 'Target Variable:',
    "pt_BR": 'Variável alvo:',
  },
  'dataset.form.target_unused': {
    "en_US": 'Target Variable: (not used)',
    "pt_BR": 'Variável alvo: (não usada)',
  },
  'dataset.form.update': {
    "en_US": 'Update Dataset',
    "pt_BR": 'Atualizar Dataset',
  },
  'dataset.handler.problem_type': {
    "en_US": 'Problem Type:',
    "pt_BR": 'Tipo de problema:',
  },
  'dataset.handler.title': {
    "en_US": 'Dataset Configuration',
    "pt_BR": 'Configuração do dataset',
  },
  'dataset.handler.train_size': {
    "en_US": 'Train Size (0 to 1):',
    "pt_BR": 'Tamanho do treino (0 a 1):',
  },
  'dataset.msg.delete_confirm': {
    "en_US": 'Delete {label} permanently?\nThis action cannot be undone.',
    "pt_BR": 'Excluir {label} permanentemente?\nEsta ação não pode ser desfeita.',
  },
  'dataset.msg.delete_partial': {
    "en_US": 'Some datasets could not be deleted (they may be used by experiments):\n\n',
    "pt_BR": 'Alguns datasets não puderam ser excluídos (podem estar em uso por experimentos):\n\n',
  },
  'dataset.msg.n_datasets': {
    "en_US": '{n} datasets',
    "pt_BR": '{n} datasets',
  },
  'dataset.msg.select_one_delete': {
    "en_US": 'Please select at least one dataset to delete.',
    "pt_BR": 'Selecione pelo menos um dataset para excluir.',
  },
  'dataset.msg.select_one_edit': {
    "en_US": 'Please select exactly one dataset to edit.',
    "pt_BR": 'Selecione exatamente um dataset para editar.',
  },
  'dataset.view.title': {
    "en_US": '📁 Datasets Library',
    "pt_BR": '📁 Biblioteca de Datasets',
  },
  'enum.analysis_output_kind.image': {
    "en_US": 'image',
    "pt_BR": 'imagem',
  },
  'enum.analysis_output_kind.scalar': {
    "en_US": 'scalar',
    "pt_BR": 'escalar',
  },
  'enum.analysis_output_kind.text': {
    "en_US": 'text',
    "pt_BR": 'texto',
  },
  'enum.experiment_status.nok': {
    "en_US": 'NOK',
    "pt_BR": 'NOK',
  },
  'enum.experiment_status.ok': {
    "en_US": 'OK',
    "pt_BR": 'OK',
  },
  'enum.experiment_status.pending': {
    "en_US": 'Pending',
    "pt_BR": 'Pendente',
  },
  'enum.learning_paradigm.supervised': {
    "en_US": 'Supervised',
    "pt_BR": 'Supervisionado',
  },
  'enum.learning_paradigm.unsupervised': {
    "en_US": 'Unsupervised',
    "pt_BR": 'Não supervisionado',
  },
  'enum.problem_type.classification': {
    "en_US": 'Classification',
    "pt_BR": 'Classificação',
  },
  'enum.problem_type.clustering': {
    "en_US": 'Clustering',
    "pt_BR": 'Agrupamento',
  },
  'enum.problem_type.dimensionality_reduction': {
    "en_US": 'Dimensionality Reduction',
    "pt_BR": 'Redução de dimensionalidade',
  },
  'enum.problem_type.regression': {
    "en_US": 'Regression',
    "pt_BR": 'Regressão',
  },
  'experiment.col.created_on': {
    "en_US": 'Created On',
    "pt_BR": 'Criado em',
  },
  'experiment.col.dataset': {
    "en_US": 'Dataset',
    "pt_BR": 'Dataset',
  },
  'experiment.col.disk': {
    "en_US": 'Disk',
    "pt_BR": 'Disco',
  },
  'experiment.col.model': {
    "en_US": 'Model',
    "pt_BR": 'Modelo',
  },
  'experiment.col.name': {
    "en_US": 'Experiment Name',
    "pt_BR": 'Nome do experimento',
  },
  'experiment.err.artifact_integrity': {
    "en_US": "Artifact '{name}' for experiment #{id} is corrupted or was modified externally (MD5 mismatch).",
    "pt_BR": "O artefato '{name}' do experimento #{id} está corrompido ou foi alterado externamente (MD5 não corresponde).",
  },
  'experiment.err.logs_integrity': {
    "en_US": 'Logs for experiment #{id} are corrupted or were modified externally (MD5 mismatch).',
    "pt_BR": 'Os logs do experimento #{id} estão corrompidos ou foram alterados externamente (MD5 não corresponde).',
  },
  'experiment.err.model_integrity': {
    "en_US": "The trained model for experiment '{name}' is corrupted or was modified externally (MD5 mismatch).",
    "pt_BR": "O modelo treinado do experimento '{name}' está corrompido ou foi alterado externamente (MD5 não corresponde).",
  },
  'experiment.err.not_found': {
    "en_US": 'Experiment with ID {id} was not found.',
    "pt_BR": 'Experimento com ID {id} não encontrado.',
  },
  'experiment.err.supervised_requires_target': {
    "en_US": 'Supervised experiments require a dataset target column.',
    "pt_BR": 'Experimentos supervisionados exigem uma coluna alvo no dataset.',
  },
  'experiment.err.target_column_missing': {
    "en_US": "Target column '{column}' not found in dataset.",
    "pt_BR": "Coluna alvo '{column}' não encontrada no dataset.",
  },
  'experiment.export.as_zip': {
    "en_US": '💾 Export as ZIP',
    "pt_BR": '💾 Export as ZIP',
  },
  'experiment.export.dialog_title': {
    "en_US": 'Export Experiment as ZIP',
    "pt_BR": 'Exportar experimento como ZIP',
  },
  'experiment.export.failed': {
    "en_US": 'Failed to export experiment:\n{error}',
    "pt_BR": 'Falha ao exportar o experimento:\n{error}',
  },
  'experiment.export.include_dataset': {
    "en_US": 'Include Dataset (.csv)',
    "pt_BR": 'Incluir dataset (.csv)',
  },
  'experiment.export.include_model': {
    "en_US": 'Include Trained Model (.pkl)',
    "pt_BR": 'Incluir modelo treinado (.pkl)',
  },
  'experiment.export.include_model_unavailable': {
    "en_US": 'Include Trained Model (.pkl)  [Not available]',
    "pt_BR": 'Incluir modelo treinado (.pkl)  [Indisponível]',
  },
  'experiment.export.include_script': {
    "en_US": 'Include Model Script (.py)',
    "pt_BR": 'Incluir script do modelo (.py)',
  },
  'experiment.export.include_script_native': {
    "en_US": 'Include Algorithm Script (.py)  [Native algorithm]',
    "pt_BR": 'Incluir script do algoritmo (.py)  [Algoritmo nativo]',
  },
  'experiment.export.select_items': {
    "en_US": 'Select items to include in the ZIP:',
    "pt_BR": 'Selecione os itens a incluir no ZIP:',
  },
  'experiment.export.success': {
    "en_US": 'Experiment exported successfully to:\n{path}',
    "pt_BR": 'Experimento exportado com sucesso para:\n{path}',
  },
  'experiment.export.title': {
    "en_US": 'Export: {name}',
    "pt_BR": 'Exportar: {name}',
  },
  'experiment.form.copy_name': {
    "en_US": '{name} (Copy)',
    "pt_BR": '{name} (Cópia)',
  },
  'experiment.form.default_name': {
    "en_US": 'Experiment #{n}',
    "pt_BR": 'Experimento #{n}',
  },
  'experiment.form.err_need_analysis': {
    "en_US": 'Select at least one analysis.',
    "pt_BR": 'Selecione pelo menos uma análise.',
  },
  'experiment.form.err_required': {
    "en_US": 'Name, Dataset, and Model are required.',
    "pt_BR": 'Nome, dataset e modelo são obrigatórios.',
  },
  'experiment.form.hyperparams': {
    "en_US": 'Hyperparameters Config',
    "pt_BR": 'Configuração de hiperparâmetros',
  },
  'experiment.form.name': {
    "en_US": 'Experiment Name:',
    "pt_BR": 'Nome do experimento:',
  },
  'experiment.form.no_analyses': {
    "en_US": 'No analyses available for this problem type.',
    "pt_BR": 'Nenhuma análise disponível para este tipo de problema.',
  },
  'experiment.form.run': {
    "en_US": 'Run Experiment',
    "pt_BR": 'Executar experimento',
  },
  'experiment.form.select_dataset': {
    "en_US": 'Select Dataset:',
    "pt_BR": 'Selecionar dataset:',
  },
  'experiment.form.select_dataset_for_analyses': {
    "en_US": 'Select a dataset to choose analyses.',
    "pt_BR": 'Selecione um dataset para escolher análises.',
  },
  'experiment.form.select_model': {
    "en_US": 'Select Model:',
    "pt_BR": 'Selecionar modelo:',
  },
  'experiment.form.title': {
    "en_US": 'New Experiment',
    "pt_BR": 'Novo experimento',
  },
  'experiment.logs.load_failed': {
    "en_US": '(Failed to load logs: {error})',
    "pt_BR": '(Falha ao carregar logs: {error})',
  },
  'experiment.logs.title': {
    "en_US": 'Execution Logs',
    "pt_BR": 'Logs de execução',
  },
  'experiment.menu.duplicate': {
    "en_US": 'Duplicate',
    "pt_BR": 'Duplicar',
  },
  'experiment.menu.view_results': {
    "en_US": 'View Results',
    "pt_BR": 'Ver resultados',
  },
  'experiment.msg.completed': {
    "en_US": 'Experiment completed successfully.',
    "pt_BR": 'Experimento concluído com sucesso.',
  },
  'experiment.msg.delete_confirm': {
    "en_US": 'Delete {label} permanently?',
    "pt_BR": 'Excluir {label} permanentemente?',
  },
  'experiment.msg.n_experiments': {
    "en_US": '{n} experiments',
    "pt_BR": '{n} experimentos',
  },
  'experiment.msg.no_results_body': {
    "en_US": 'No analysis results were found for this experiment.',
    "pt_BR": 'Nenhum resultado de análise foi encontrado para este experimento.',
  },
  'experiment.msg.no_results_title': {
    "en_US": 'No Results',
    "pt_BR": 'Sem resultados',
  },
  'experiment.msg.pipeline_error': {
    "en_US": 'Error executing pipeline:\n\n{error}\n\nTry checking if your hyperparameters are valid.',
    "pt_BR": 'Erro ao executar o pipeline:\n\n{error}\n\nVerifique se os hiperparâmetros são válidos.',
  },
  'experiment.msg.select_delete': {
    "en_US": 'Select at least one experiment to delete.',
    "pt_BR": 'Selecione pelo menos um experimento para excluir.',
  },
  'experiment.msg.select_one_duplicate': {
    "en_US": 'Select exactly one experiment to duplicate.',
    "pt_BR": 'Selecione exatamente um experimento para duplicar.',
  },
  'experiment.msg.select_one_export': {
    "en_US": 'Select exactly one experiment to export.',
    "pt_BR": 'Selecione exatamente um experimento para exportar.',
  },
  'experiment.msg.select_one_results': {
    "en_US": 'Select exactly one experiment to view results.',
    "pt_BR": 'Selecione exatamente um experimento para ver os resultados.',
  },
  'experiment.results.title': {
    "en_US": 'Results: {name}',
    "pt_BR": 'Resultados: {name}',
  },
  'experiment.status.nok': {
    "en_US": '❌ NOK',
    "pt_BR": '❌ NOK',
  },
  'experiment.status.ok': {
    "en_US": '✅ OK',
    "pt_BR": '✅ OK',
  },
  'experiment.status.pending': {
    "en_US": '⏳ Pending',
    "pt_BR": '⏳ Pending',
  },
  'experiment.view.title': {
    "en_US": '🧪 Experiments',
    "pt_BR": '🧪 Experimentos',
  },
  'model.col.name': {
    "en_US": 'Model Name',
    "pt_BR": 'Nome do modelo',
  },
  'model.col.problem_type': {
    "en_US": 'Problem Type',
    "pt_BR": 'Tipo de problema',
  },
  'model.err.native_cannot_delete': {
    "en_US": 'Native models cannot be deleted.',
    "pt_BR": 'Modelos nativos não podem ser removidos.',
  },
  'model.hyperparams.empty': {
    "en_US": 'No hyperparameters available.',
    "pt_BR": 'Nenhum hiperparâmetro disponível.',
  },
  'model.hyperparams.invalid_value': {
    "en_US": 'Invalid value for {label}. Expected {type}.',
    "pt_BR": 'Valor inválido para {label}. Esperado {type}.',
  },
  'model.hyperparams.readonly': {
    "en_US": 'Hyperparameters (Read-Only)',
    "pt_BR": 'Hiperparâmetros (somente leitura)',
  },
  'model.msg.cannot_update_native': {
    "en_US": 'You cannot update native models.',
    "pt_BR": 'Não é possível atualizar modelos nativos.',
  },
  'model.msg.delete_confirm': {
    "en_US": 'Delete {label} permanently?{extra}\nThis will permanently remove the plugin file(s).',
    "pt_BR": 'Excluir {label} permanentemente?{extra}\nIsso removerá permanentemente o(s) arquivo(s) do plugin.',
  },
  'model.msg.delete_partial': {
    "en_US": 'Some models could not be deleted:\n\n',
    "pt_BR": 'Alguns modelos não puderam ser excluídos:\n\n',
  },
  'model.msg.imported': {
    "en_US": 'Successfully imported: {names}',
    "pt_BR": 'Importado com sucesso: {names}',
  },
  'model.msg.n_models': {
    "en_US": '{n} models',
    "pt_BR": '{n} modelos',
  },
  'model.msg.select_delete': {
    "en_US": 'Please select at least one model to delete.',
    "pt_BR": 'Selecione pelo menos um modelo para excluir.',
  },
  'model.msg.select_one_update': {
    "en_US": 'Please select exactly one custom model to update.',
    "pt_BR": 'Selecione exatamente um modelo personalizado para atualizar.',
  },
  'model.msg.select_updated_py': {
    "en_US": 'Select updated .py for {name}',
    "pt_BR": 'Selecione o .py atualizado para {name}',
  },
  'model.msg.skip_native': {
    "en_US": '({n} native model(s) will be skipped.)',
    "pt_BR": '({n} modelo(s) nativo(s) serão ignorados.)',
  },
  'model.msg.updated': {
    "en_US": 'Successfully updated: {names}',
    "pt_BR": 'Atualizado com sucesso: {names}',
  },
  'model.view.title': {
    "en_US": '🧠 Models Library',
    "pt_BR": '🧠 Biblioteca de Modelos',
  },
  'nav.analyses': {
    "en_US": '📈 Analyses',
    "pt_BR": '📈 Análises',
  },
  'nav.datasets': {
    "en_US": '📁 Datasets',
    "pt_BR": '📁 Datasets',
  },
  'nav.models': {
    "en_US": '🧠 Models',
    "pt_BR": '🧠 Modelos',
  },
  'nav.settings': {
    "en_US": '⚙ Settings',
    "pt_BR": '⚙ Configurações',
  },
  'settings.language': {
    "en_US": 'Language',
    "pt_BR": 'Idioma',
  },
  'settings.storage.analyses': {
    "en_US": 'Analyses',
    "pt_BR": 'Análises',
  },
  'settings.storage.app_data': {
    "en_US": 'App data',
    "pt_BR": 'Dados do app',
  },
  'settings.storage.app_total': {
    "en_US": 'App total',
    "pt_BR": 'Total do app',
  },
  'settings.storage.app_vs_disk': {
    "en_US": 'App vs disk',
    "pt_BR": 'App vs Disco',
  },
  'settings.storage.computer_disk': {
    "en_US": 'Computer disk',
    "pt_BR": 'Disco do computador',
  },
  'settings.storage.database': {
    "en_US": 'Database',
    "pt_BR": 'Banco de dados',
  },
  'settings.storage.datasets': {
    "en_US": 'Datasets',
    "pt_BR": 'Datasets',
  },
  'settings.storage.disk_free': {
    "en_US": 'Disk free',
    "pt_BR": 'Disco livre',
  },
  'settings.storage.disk_total': {
    "en_US": 'Disk total',
    "pt_BR": 'Disco total',
  },
  'settings.storage.disk_used': {
    "en_US": 'Disk used',
    "pt_BR": 'Disco usado',
  },
  'settings.storage.experiments': {
    "en_US": 'Experiments',
    "pt_BR": 'Experimentos',
  },
  'settings.storage.models': {
    "en_US": 'Models',
    "pt_BR": 'Modelos',
  },
  'settings.storage.other': {
    "en_US": 'Other',
    "pt_BR": 'Outros',
  },
  'settings.storage.title': {
    "en_US": 'Application Storage',
    "pt_BR": 'Armazenamento do Aplicativo',
  },
  'settings.title': {
    "en_US": 'Settings',
    "pt_BR": 'Configurações',
  },
}

ENGLISH_TO_CODE: dict[str, str] = {v["en_US"]: k for k, v in MESSAGES.items()}
