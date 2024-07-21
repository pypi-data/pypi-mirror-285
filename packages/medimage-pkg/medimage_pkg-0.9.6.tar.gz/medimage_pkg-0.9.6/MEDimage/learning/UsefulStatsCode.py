def bootstrapped_confidence_interval(self, metric: str = 'AUC', n_bootstrap: int = 1000) -> Tuple[float, float]:
        """
        Computes the bootstrapped confidence interval for the given metric.

        Args:
            metric (str, optional): Metric to use for comparison. Defaults to 'AUC'.
            n_bootstrap (int, optional): Number of bootstrap samples. Defaults to 1000.
        
        Returns:
            Tuple[float, float]: Lower and upper bounds of the confidence interval.
        """
        # Load outcomes dataframe
        try:
            outcomes = pd.read_csv(self.path_experiment / "outcomes.csv", sep=',')
        except:
            outcomes = pd.read_csv(self.path_experiment.parent / "outcomes.csv", sep=',')

        # Initialization
        predictions_one_all = list()
        predictions_two_all = list()
        patients_ids_all = list()
        test = self.path_experiment / f'learn__{self.experiment}_{self.levels[0]}_{self.modalities[0]}'
        nb_split = len([x[0] for x in os.walk(self.path_experiment / f'learn__{self.experiment}_{self.levels[0]}_{self.modalities[0]}')]) - 1

        list_folds = [Path(x[0]) for x in os.walk(test)][1:]
        metrics_all = []

        for fold in list_folds:
            if (fold / 'run_results.json').exists():
                results = load_json(fold / 'run_results.json')
                metrics_all.append(results[list(results.keys())[0]]['test']['metrics'][metric])

        confidence_interval_metrics = np.percentile(metrics_all, [2.5, 97.5])
        
        # For each split
        for i in range(1, nb_split + 1):
            # Get predictions and patients ids
            patients_ids, predictions_one, predictions_two = self.__get_patients_and_predictions(i)
            
            # Add-up all information
            predictions_one_all.extend(predictions_one)
            #predictions_two_all.extend(predictions_two)
            patients_ids_all.extend(patients_ids)
        
        # Get ground truth for selected patients
        ground_truth = []
        for patient in patients_ids_all:
            ground_truth.append(outcomes[outcomes['PatientID'] == patient][outcomes.columns[-1]].values[0])

        # to numpy array
        ground_truth = np.array(ground_truth)

        # Step 2: Bootstrap sampling on validation predictions
        bootstrap_metrics = []
        for _ in range(n_bootstrap):
            bootstrap_indices = np.random.choice(len(predictions_one_all), size=len(predictions_one_all), replace=True)
            bootstrap_predictions = [predictions_one_all[i] for i in bootstrap_indices]
            bootstrap_labels = [ground_truth[i] for i in bootstrap_indices]
            
            # Compute AUC for bootstrap sample
            auc = metrics.roc_auc_score(bootstrap_labels, bootstrap_predictions)
            bootstrap_metrics.append(auc)

        # Step 3: Calculate confidence intervals
        confidence_interval = np.percentile(bootstrap_metrics, [2.5, 97.5])

        return confidence_interval