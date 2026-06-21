import React, { useState } from 'react';
import { View, TouchableOpacity, Text, StyleSheet, Animated } from 'react-native';
import { Ionicons } from '@expo/vector-icons';

interface ButtonChild {
  id: string;
  label: string;
  icon: string;
  color: string;
  onPress: () => void;
}

interface ExpandableButtonGroupProps {
  parentId: string;
  parentLabel: string;
  parentIcon: string;
  parentColor: string;
  children: ButtonChild[];
  onParentPress?: () => void;
}

export const ExpandableButtonGroup: React.FC<ExpandableButtonGroupProps> = ({
  parentId,
  parentLabel,
  parentIcon,
  parentColor,
  children,
  onParentPress,
}) => {
  const [expanded, setExpanded] = useState(false);
  const [selectedChildId, setSelectedChildId] = useState<string | null>(null);

  const handleParentPress = () => {
    setExpanded(!expanded);
    onParentPress?.();
  };

  const handleChildPress = (child: ButtonChild) => {
    setSelectedChildId(child.id);
    // Glow pulse effect — auto-deselect after animation
    setTimeout(() => setSelectedChildId(null), 3000);
    child.onPress();
    setExpanded(false);
  };

  return (
    <View style={st.container}>
      {/* Parent Button */}
      <TouchableOpacity
        onPress={handleParentPress}
        activeOpacity={0.7}
        style={[
          st.parentBtn,
          {
            backgroundColor: 'rgba(0,0,0,0.6)',
            borderColor: parentColor,
            shadowColor: parentColor,
            shadowOpacity: selectedChildId === parentId ? 0.8 : 0.4,
            shadowRadius: selectedChildId === parentId ? 20 : 8,
          },
        ]}
      >
        {parentIcon.startsWith('emoji') ? (
          <Text style={{ fontSize: 22 }}>🚗</Text>
        ) : (
          <Ionicons name={parentIcon as any} size={22} color={parentColor} />
        )}
        <Text style={[st.parentLabel, { color: parentColor }]}>{parentLabel}</Text>
      </TouchableOpacity>

      {/* Child Buttons — appear when expanded */}
      {expanded && (
        <View style={st.childrenContainer}>
          {children.map((child, idx) => (
            <TouchableOpacity
              key={child.id}
              onPress={() => handleChildPress(child)}
              activeOpacity={0.7}
              style={[
                st.childBtn,
                {
                  backgroundColor: 'rgba(0,0,0,0.6)',
                  borderColor: child.color,
                  shadowColor: child.color,
                  shadowOpacity: selectedChildId === child.id ? 0.8 : 0.4,
                  shadowRadius: selectedChildId === child.id ? 16 : 6,
                  // Stagger animation
                  opacity: expanded ? 1 : 0,
                  transform: [{ scale: expanded ? 1 : 0.5 }],
                },
              ]}
            >
              <Ionicons name={child.icon as any} size={18} color={child.color} />
              <Text style={[st.childLabel, { color: child.color }]}>{child.label}</Text>
            </TouchableOpacity>
          ))}
        </View>
      )}
    </View>
  );
};

const st = StyleSheet.create({
  container: {
    alignItems: 'center',
    marginBottom: 16,
  },
  parentBtn: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 8,
    borderRadius: 14,
    borderWidth: 1.5,
    paddingVertical: 14,
    paddingHorizontal: 12,
    minWidth: 90,
    justifyContent: 'center',
    shadowOffset: { width: 0, height: 2 },
    elevation: 4,
  },
  parentLabel: {
    fontSize: 12,
    fontWeight: '600',
    textAlign: 'center',
  },
  childrenContainer: {
    marginTop: 8,
    gap: 8,
  },
  childBtn: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 6,
    borderRadius: 12,
    borderWidth: 1,
    paddingVertical: 10,
    paddingHorizontal: 10,
    justifyContent: 'center',
    shadowOffset: { width: 0, height: 2 },
    elevation: 3,
  },
  childLabel: {
    fontSize: 11,
    fontWeight: '600',
  },
});
