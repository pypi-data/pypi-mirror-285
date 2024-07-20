class FeatureService:
    def __init__(self):
        self.features = {}

    def add_feature(self, feature_name: str, feature_impl):
        self.features[feature_name] = feature_impl

    def run_feature(self, feature_name: str, input_data: str) -> str:
        if feature_name in self.features:
            return self.features[feature_name](input_data)
        return "Feature not found."